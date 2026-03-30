# -*- coding: utf-8 -*-
"""
Created on Wed Dec  3 16:08:54 2025

@author: Sri.Sakthivel
"""

import can
import time
import os
import sys
import json
import logging


# Set the 'can' logger to only show errors
logging.getLogger("can").setLevel(logging.ERROR)
# Optionally also keep the root logger quiet
logging.basicConfig(level=logging.ERROR)


def log_message(direction, msg):
    """
    Log only the diagnostics frames we care about.

    - Tx: always show the request
    - Rx: only show the response with arbitration_id 0x7F1 (the positive reply)
    """
    # For Tx, always print
    if direction == "Tx":
        data_str = " ".join(f"{byte:02X}" for byte in msg.data)
        print(f"{direction} {msg.arbitration_id:03X} {msg.dlc} {data_str}")
        return

    # For Rx, print only if it is the diagnostic response we expect (0x7F1)
    if direction == "Rx" and msg.arbitration_id == 0x7F1:
        data_str = " ".join(f"{byte:02X}" for byte in msg.data)
        print(f"{direction} {msg.arbitration_id:03X} {msg.dlc} {data_str}")


def _load_can_config():
    try:
        base_dir = getattr(
            sys, "_MEIPASS", os.path.abspath(os.path.dirname(sys.argv[0]))
        )
    except Exception:
        base_dir = os.path.abspath(".")

    config_path = os.path.join(base_dir, "config.json")

    iface = "PCAN_USBBUS1"
    bitrate = 500000

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            cfg = json.load(f)
        iface = str(cfg.get("can_interface", iface))
        bitrate = int(cfg.get("can_bitrate", bitrate))
    except Exception:
        pass

    return iface, bitrate


def _config_socketcan(interface: str, bitrate: int = 500000):
    os.system(f"sudo ip link set {interface} down")
    os.system(f"sudo ip link set {interface} up type can bitrate {bitrate}")


def _open_bus():
    iface, bitrate = _load_can_config()
    iface_upper = iface.upper()

    if iface_upper.startswith("PCAN"):
        bus = can.interface.Bus(
            channel=iface, bustype="pcan", bitrate=bitrate, fd=False
        )
        print(f"CAN bus initialized (PCAN, channel={iface}, bitrate={bitrate}).")

    elif iface.lower().startswith("can"):
        _config_socketcan(interface=iface, bitrate=bitrate)
        bus = can.interface.Bus(
            channel=iface, bustype="socketcan", bitrate=bitrate
        )
        print(f"CAN bus initialized (SocketCAN, channel={iface}, bitrate={bitrate}).")

    else:
        raise ValueError(f"Unsupported CAN interface in config: {iface}")

    return bus, iface, bitrate


def Battery_Voltage():
    bus = None
    try:
        # Open bus based on config.json (PCAN or SocketCAN)
        bus, iface, bitrate = _open_bus()

        # Request: 03 22 E1 42
        request = can.Message(
            arbitration_id=0x7F0,
            data=[0x03, 0x22, 0xE1, 0x42, 0x00, 0x00, 0x00, 0x00],
            is_extended_id=False,
        )
        log_message("Tx", request)
        bus.send(request)

        # Wait for response up to 2 seconds
        start_time = time.time()
        while time.time() - start_time < 2.0:
            response = bus.recv(timeout=0.5)
            if response:
                # Only log the Rx frame if it is the diagnostic reply (0x7F1)
                log_message("Rx", response)

                # Check for positive response 62 E1 42 at ID 0x7F1
                if (
                    response.arbitration_id == 0x7F1
                    and len(response.data) >= 5
                    and response.data[1] == 0x62
                    and response.data[2] == 0xE1
                    and response.data[3] == 0x42
                ):
                    voltage = response.data[4] * 0.1  # scaling: 0.1 V per bit
                    formatted = f"{voltage:.1f} V"
                    print("Battery Voltage Reading:", formatted)
                    return True, formatted

        print("No response received.")
        return False, "No response"

    except can.CanError as e:
        msg = f"CAN Error: {e}"
        print(msg)
        return False, msg

    except ValueError as e:
        msg = f"Configuration error: {e}"
        print(msg)
        return False, msg

    finally:
        if bus is not None:
            try:
                bus.shutdown()
            except Exception:
                pass
            print("CAN bus shutdown.")


if __name__ == "__main__":
    Battery_Voltage()
