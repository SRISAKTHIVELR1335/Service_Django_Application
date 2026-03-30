# -*- coding: utf-8 -*-
"""
Created on Wed Nov  5 14:10:43 2025
@author: Sri.Sakthivel
"""

import can
import time
import os
import sys
import json
from can import Message

TESTER_ID = 0x7F0
ECU_RESPONSE_ID = 0x7F1

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
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
        # If config.json is missing or invalid, defaults are used.
        pass
    return can_interface, can_bitrate

def can_config(interface="can0", bitrate=500000):
    os.system(f"sudo ip link set {interface} down")
    os.system(f"sudo ip link set {interface} up type can bitrate {bitrate}")

def log_message(direction, msg):
    formatted_data = ' '.join(f'{byte:02X}' for byte in msg.data)
    print(f"{direction} {msg.arbitration_id:04X}: {formatted_data}")

def _send_can_frame(bus, arbitration_id, data):
    padded_data = list(data)
    while len(padded_data) < 8:
        padded_data.append(0x00)
    msg = Message(arbitration_id=arbitration_id,data=bytearray(padded_data[:8]),is_fd=False,is_extended_id=False,)
    log_message("TX", msg)
    bus.send(msg)


def _receive_single_can_frame(bus, response_id, timeout=0.5):
    start_time = time.time()
    while time.time() - start_time < timeout:
        msg = bus.recv(timeout=timeout - (time.time() - start_time))
        if msg and msg.arbitration_id == response_id:
            log_message("RX", msg)
            return msg
    return None


def receive_isotp_response(bus, response_id, timeout=5.0):
    start_time = time.time()
    full_response_data = []
    expect_consecutive_frames = False
    seq_number_expected = 1
    total_uds_length = 0

    while time.time() - start_time < timeout:
        msg = _receive_single_can_frame(bus, response_id, timeout=0.5)
        if not msg:
            continue

        pci_type = (msg.data[0] & 0xF0) >> 4

        if pci_type == 0x0:  # Single Frame
            uds_length = msg.data[0] & 0x0F
            full_response_data = list(msg.data[1:1 + uds_length])
            break

        elif pci_type == 0x1:  # First Frame
            total_uds_length = ((msg.data[0] & 0x0F) << 8) + msg.data[1]
            print(f"Total UDS length expected: {total_uds_length}")
            full_response_data = list(msg.data[2:])
            expect_consecutive_frames = True
            seq_number_expected = 1

            # Send Flow Control
            fc_frame = [0x30, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
            time.sleep(0.01)
            _send_can_frame(bus, TESTER_ID, fc_frame)
            time.sleep(0.01)
            continue

        elif expect_consecutive_frames and pci_type == 0x2:  # Consecutive Frame
            seq_number = msg.data[0] & 0x0F
            if seq_number != seq_number_expected:
                print(f"ISO-TP Sequence mismatch. Expected: {seq_number_expected}, Got: {seq_number}")
                return None
            full_response_data.extend(msg.data[1:])
            seq_number_expected = (seq_number_expected + 1) % 16

            if len(full_response_data) >= total_uds_length:
                full_response_data = full_response_data[:total_uds_length]
                break
            continue

    if not full_response_data:
        return None
    return full_response_data

def send_isotp_request(bus, arbitration_id, data):
    total_len = len(data)
    if total_len <= 7:
        sf = [total_len] + data + [0x00] * (7 - total_len)
        _send_can_frame(bus, arbitration_id, sf)
        return True

    # Send First Frame
    ff_data = [0x10 | ((total_len >> 8) & 0x0F), total_len & 0xFF] + data[:6]
    _send_can_frame(bus, arbitration_id, ff_data)

    # Wait for Flow Control
    fc_msg = _receive_single_can_frame(bus, ECU_RESPONSE_ID, timeout=1.0)
    if not fc_msg:
        print("No flow control received.")
        return False

    pci_type = (fc_msg.data[0] & 0xF0) >> 4
    if pci_type != 0x3:
        print("Invalid flow control frame.")
        return False

    flow_status = fc_msg.data[0] & 0x0F
    st_min = fc_msg.data[2]

    if st_min <= 127:
        st_min_sec = st_min * 0.001
    elif 0xF1 <= st_min <= 0xF9:
        st_min_sec = (st_min - 0xF0) * 0.0001
    else:
        print("Reserved st_min value, using default 0.001")
        st_min_sec = 0.001

    if flow_status != 0:  # Not Clear to Send
        print(f"Flow control status not CTS: {flow_status}")
        return False

    # Send Consecutive Frames
    remaining_data = data[6:]
    seq = 1
    while remaining_data:
        time.sleep(st_min_sec)
        cf_pci = 0x20 | (seq % 16)
        cf_data_len = min(7, len(remaining_data))
        cf_data = [cf_pci] + remaining_data[:cf_data_len]
        _send_can_frame(bus, arbitration_id, cf_data)
        remaining_data = remaining_data[cf_data_len:]
        seq += 1

    return True

def send_uds_request(bus, sid, sub_payload, expected_positive_sid):
    uds_payload = [sid] + sub_payload
    max_retries = 3
    retry_delay = 5.0  # Wait 5 seconds for NRC 0x78
    isotp_sf_data = None

    # Send the initial request
    if len(uds_payload) <= 7:
        isotp_sf_data = [len(uds_payload)] + uds_payload
        _send_can_frame(bus, TESTER_ID, isotp_sf_data)
    else:
        if not send_isotp_request(bus, TESTER_ID, uds_payload):
            print("Failed to send ISO-TP request.")
            return None

    # Retry loop for receiving response
    for attempt in range(max_retries):
        response = receive_isotp_response(bus, ECU_RESPONSE_ID, timeout=5.0)
        if response and response[0] == 0x7F:
            if len(response) >= 3 and response[2] == 0x78:
                time.sleep(retry_delay)
                continue
            if len(response) >= 3:
                print(f"Negative Response: NRC 0x{response[2]:02X}")
            return None

        if response and response[0] == expected_positive_sid:
            return response

        if attempt < max_retries - 1:
            # Resend the request only if we need to retry
            if len(uds_payload) <= 7:
                if isotp_sf_data is None:
                    isotp_sf_data = [len(uds_payload)] + uds_payload
                _send_can_frame(bus, TESTER_ID, isotp_sf_data)
            else:
                if not send_isotp_request(bus, TESTER_ID, uds_payload):
                    print(f"Attempt {attempt + 1}: Failed to resend ISO-TP request.")
                    return None
            time.sleep(retry_delay)

    print(f"Failed after {max_retries} attempts.")
    return None

def extended_diagnostic_session(bus):
    response = send_uds_request(bus, 0x10, [0x03], 0x50)
    if response and len(response) >= 2 and response[1] == 0x03:
        print("Extended Diagnostic Session Passed.\n")
        return True
    print("Extended Diagnostic Session Failed.")
    return False


def Read_Vin_Number(bus=None):
    local_bus = bus
    created_local_bus = False

    if local_bus is None:
        try:
            can_interface, can_bitrate = load_can_config()
            iface_upper = can_interface.upper()

            if iface_upper.startswith("PCAN"):
                # PCAN bus
                local_bus = can.interface.Bus(interface="pcan",channel=can_interface,bitrate=can_bitrate,fd=False)
                print(f"Initialized local PCAN bus (channel={can_interface}, bitrate={can_bitrate}).")

            elif can_interface.lower().startswith("can"):
                # SocketCAN bus
                can_config(interface=can_interface, bitrate=can_bitrate)
                local_bus = can.interface.Bus(interface="socketcan",channel=can_interface,bitrate=can_bitrate)
                print(f"Initialized local SocketCAN bus (channel={can_interface}, bitrate={can_bitrate}).")

            else:
                print(f"Unsupported CAN interface in config: {can_interface}")
                return (False, None)

            local_bus.set_filters([{"can_id": ECU_RESPONSE_ID, "can_mask": 0x7FF}])
            created_local_bus = True

        except Exception as e:
            print(f"Failed to initialize CAN bus from config: {e}")
            return (False, None)

    try:
        if not extended_diagnostic_session(local_bus):
            return (False, None)

        response = send_uds_request(local_bus, 0x22, [0xF1, 0x90], 0x62)
        if response and len(response) >= 3 and response[1] == 0xF1 and response[2] == 0x90:
            vin_raw = response[3:]
            vin_str = ''.join(chr(b) if 32 <= b <= 126 else '0' for b in vin_raw)
            print("Read Data By Identifier Passed.\n")
            formatted = f"{vin_str}"
            return True, formatted

        print("Read Data By Identifier Failed.")
        return (False, None)

    except Exception as e:
        print(f"Error in Read_Vin_Number: {e}")
        import traceback
        traceback.print_exc()
        return (False, None)

    finally:
        # Shutdown only if we created a local bus
        if created_local_bus and local_bus is not None:
            try:
                local_bus.shutdown()
            except Exception:
                pass
            print("Local CAN bus shutdown completed")


def main():
    bus = None
    try:
        can_interface, can_bitrate = load_can_config()
        iface_upper = can_interface.upper()

        if iface_upper.startswith("PCAN"):
            bus = can.interface.Bus(interface="pcan",channel=can_interface,bitrate=can_bitrate,fd=False)
            print(f"CAN bus initialized (PCAN, channel={can_interface}, bitrate={can_bitrate}).")

        elif can_interface.lower().startswith("can"):
            can_config(interface=can_interface, bitrate=can_bitrate)
            bus = can.interface.Bus(interface="socketcan",channel=can_interface,bitrate=can_bitrate)
            print(f"CAN bus initialized (SocketCAN, channel={can_interface}, bitrate={can_bitrate}).")

        else:
            print(f"Unsupported CAN interface in config: {can_interface}")
            return

        bus.set_filters([{"can_id": ECU_RESPONSE_ID, "can_mask": 0x7FF}])

        if not extended_diagnostic_session(bus):
            return

        result = Read_Vin_Number(bus)  # Pass bus to function
        print(f"Final Result: {result}")

    except can.CanError as e:
        print(f"CAN Bus Error: {e}")
        
    except Exception as e:
        print(f"Unexpected Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if bus:
            try:
                bus.shutdown()
            except Exception:
                pass
            print("CAN bus shutdown completed")


if __name__ == "__main__":
    main()