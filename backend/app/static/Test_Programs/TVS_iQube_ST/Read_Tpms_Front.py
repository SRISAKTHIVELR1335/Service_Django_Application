import can
from can.message import Message
import time
import os
import sys
import json


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS  # type: ignore[attr-defined]
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


CONFIG_PATH = resource_path("config.json")


def load_can_config():
    can_interface = "PCAN_USBBUS1"
    can_bitrate = 500000
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            cfg = json.load(f)
        can_interface = str(cfg.get("can_interface", can_interface))
        can_bitrate = int(cfg.get("can_bitrate", can_bitrate))
    except Exception:
        pass
    return can_interface, can_bitrate


def can_config(interface="can0", bitrate=500000):
    os.system(f"sudo ip link set {interface} down")
    os.system(f"sudo ip link set {interface} up type can bitrate {bitrate} ")


def log_message(direction, msg):
    formatted_data = ' '.join(f'{byte:02X}' for byte in msg.data)
    print(f"{direction} {msg.arbitration_id:04X} {msg.dlc} {formatted_data}")


def parse_mac_from_payload(data_bytes):
    data = bytes(data_bytes)
    if len(data) >= 7:
        cmd = data[0]
        if cmd in (0x01, 0x02):
            mac_bytes = data[1:7]
            if any(b != 0x00 for b in mac_bytes):  # Avoid trivial all-zero MAC
                return ''.join(f'{b:02X}' for b in mac_bytes)
    # Fallback: scan for any consecutive 6 non-zero bytes
    for i in range(0, max(0, len(data) - 5)):
        segment = data[i:i+6]
        if any(b != 0x00 for b in segment):
            return ''.join(f'{b:02X}' for b in segment)
    return None


def flush_can_buffer(bus, flush_time=0.3):
    end = time.time() + flush_time
    while time.time() < end:
        msg = bus.recv(timeout=0.01)
        if msg is None:
            break


def Read_Tpms_Front(expected_mac, interface="PCAN_USBBUS1", bitrate=500000, timeout=5):
    print("TEST SEQUENCE : Read_Tpms_Front")

    if not expected_mac or len(expected_mac) != 12:
        print(f"Invalid expected MAC: {expected_mac}")
        return (False, None)

    expected_mac = expected_mac.upper()
    expected_bytes = [int(expected_mac[i:i+2], 16) for i in range(0, len(expected_mac), 2)]

    bus = None
    try:
        # Read interface selection from config.json
        cfg_iface, cfg_bitrate = load_can_config()
        iface_upper = cfg_iface.upper()

        if iface_upper.startswith("PCAN"):
            # PCAN path
            bus = can.interface.Bus(interface="pcan",channel=cfg_iface,bitrate=cfg_bitrate,fd=False)
            print(f"CAN bus initialized (PCAN, channel={cfg_iface}, bitrate={cfg_bitrate}).")

        elif cfg_iface.lower().startswith("can"):
            # SocketCAN path
            can_config(interface=cfg_iface, bitrate=cfg_bitrate)
            bus = can.interface.Bus(interface="socketcan",channel=cfg_iface,bitrate=cfg_bitrate)
            print(f"CAN bus initialized (SocketCAN, channel={cfg_iface}, bitrate={cfg_bitrate}).")

        else:
            print(f"Unsupported CAN interface in config: {cfg_iface}")
            return (False, None)

        # Send targeted read request: [0x02 + expected_MAC_bytes (6) + 0x00] on 0x7F3
        req_payload = bytearray([0x02] + expected_bytes[:6] + [0x00])  # 6 MAC bytes + pad
        req_msg = Message(arbitration_id=0x7F3, data=req_payload, is_fd=False, is_extended_id=False)
        log_message("Tx", req_msg)
        bus.send(req_msg)

        # Set filter to only receive relevant responses
        bus.set_filters([{"can_id": 0x7F1, "can_mask": 0x7FF, "extended": False}])

        # Flush old messages to avoid random frames
        flush_can_buffer(bus)

        start = time.time()
        while True:
            remaining = timeout - (time.time() - start)
            if remaining <= 0:
                break

            resp = bus.recv(timeout=max(0.1, remaining))
            if resp is None:
                continue

            if resp.arbitration_id != 0x7F1:
                continue

            log_message("Rx", resp)

            # Parse payload for 6-byte MAC
            actual_mac = parse_mac_from_payload(resp.data)
            if actual_mac:
                success = (actual_mac.upper() == expected_mac)
                status = "PASSED" if success else "FAILED (mismatch)"
                print(f"Read_Tpms_Front: {status} - Read MAC: {actual_mac}, Expected: {expected_mac}")
                return (success, actual_mac.upper())  # Tuple: match success, actual MAC

        print("Read_Tpms_Front: No valid response or MAC not found within timeout.")
        return (False, None)

    except can.CanError as e:
        print(f"CAN error: {e}")
        return (False, None)

    except Exception as e:
        print(f"Unexpected error: {e}")
        return (False, None)

    finally:
        if bus is not None:
            try:
                bus.shutdown()
            except Exception:
                pass
            print("CAN bus shutdown.")


if __name__ == "__main__":
    Read_Tpms_Front("C03687540000", timeout=5)