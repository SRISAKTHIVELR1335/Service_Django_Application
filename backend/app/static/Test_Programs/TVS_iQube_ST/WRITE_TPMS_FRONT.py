# -*- coding: utf-8 -*-
"""
Created on Mon Aug 11 15:45:15 2025

@author: Sri.Sakthivel
"""

import can
import os
import sys
import json
import logging
from can.message import Message


# -------------------------------------------------------------------------
# Reduce python-can noise (e.g. "uptime library not available...")
# -------------------------------------------------------------------------
logging.getLogger("can").setLevel(logging.ERROR)
logging.basicConfig(level=logging.ERROR)


def resource_path(relative_path: str) -> str:
    """Get absolute path to resource, works for dev and PyInstaller."""
    try:
        base_path = sys._MEIPASS  # type: ignore[attr-defined]
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


CONFIG_PATH = resource_path("config.json")


def load_can_config():
    """
    Read CAN interface settings from config.json.

    Expected keys:
      - "can_interface": e.g. "PCAN_USBBUS1" or "can0"
      - "can_bitrate" : e.g. 500000
    """
    can_interface = "PCAN_USBBUS1"
    can_bitrate = 500000
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            cfg = json.load(f)
        can_interface = str(cfg.get("can_interface", can_interface))
        can_bitrate = int(cfg.get("can_bitrate", can_bitrate))
    except Exception:
        # fall back to defaults if anything fails
        pass
    return can_interface, can_bitrate


def can_config(interface: str = "can0", bitrate: int = 500000) -> None:
    """Configure SocketCAN interface on Linux."""
    os.system(f"sudo ip link set {interface} down")
    os.system(f"sudo ip link set {interface} up type can bitrate {bitrate}")


def log_message(direction, msg: Message) -> None:
    """
    Log only what we care about:

      - Tx: always show the request
      - Rx: only show the diagnostic response (ID 0x7F1)
    """
    if direction == "Tx":
        formatted_data = " ".join(f"{byte:02X}" for byte in msg.data)
        print(f"{direction} {msg.arbitration_id:04X} {msg.dlc} {formatted_data}")
        return

    if direction == "Rx" and msg.arbitration_id == 0x7F1:
        formatted_data = " ".join(f"{byte:02X}" for byte in msg.data)
        print(f"{direction} {msg.arbitration_id:04X} {msg.dlc} {formatted_data}")


def WRITE_TPMS_FRONT(front_mac: str):
    """
    Write TPMS Front MAC ID.

    Returns:
      (True, <MAC_UPPER>) on success,
      (False, None) on failure.
    """
    print("TEST SEQUENCE : WRITE_TPMS_FRONT")

    # Validate MAC: 12 hex characters
    if (
        not front_mac
        or len(front_mac) != 12
        or not all(c in "0123456789ABCDEFabcdef" for c in front_mac)
    ):
        print(f"Invalid MAC address: {front_mac}")
        return (False, None)

    bus = None
    try:
        cfg_iface, cfg_bitrate = load_can_config()
        iface_upper = cfg_iface.upper()

        # ------------------------------------------------------------------
        # Select CAN backend from config.json: PCAN or SocketCAN
        # ------------------------------------------------------------------
        if iface_upper.startswith("PCAN"):
            # PCAN
            bus = can.interface.Bus(
                interface="pcan",
                channel=cfg_iface,
                bitrate=cfg_bitrate,
                fd=False,
            )
            print(
                f"CAN bus initialized (PCAN, channel={cfg_iface}, "
                f"bitrate={cfg_bitrate})."
            )

        elif cfg_iface.lower().startswith("can"):
            # SocketCAN
            can_config(interface=cfg_iface, bitrate=cfg_bitrate)
            bus = can.interface.Bus(
                interface="socketcan",
                channel=cfg_iface,
                bitrate=cfg_bitrate,
            )
            print(
                f"CAN bus initialized (SocketCAN, channel={cfg_iface}, "
                f"bitrate={cfg_bitrate})."
            )

        else:
            print(f"Unsupported CAN interface in config: {cfg_iface}")
            return (False, None)

        # ------------------------------------------------------------------
        # Build payload: [0x01] + MAC bytes + [0x00]
        # (same as your simple example, but configurable now)
        # ------------------------------------------------------------------
        mac_bytes = [int(front_mac[i : i + 2], 16) for i in range(0, len(front_mac), 2)]
        full_payload = [0x01] + mac_bytes + [0x00]

        # NOTE: you used arbitration_id=0x7F3 in your simple example.
        # Keeping that here. Change to 0x7F0 if your ECU expects 0x7F0 instead.
        message = Message(
            arbitration_id=0x7F3,
            data=bytearray(full_payload),
            is_fd=False,
            is_extended_id=False,
        )
        log_message("Tx", message)
        bus.send(message)

        # Listen for response on 0x7F1
        bus.set_filters([{"can_id": 0x7F1, "can_mask": 0x7FF, "extended": False}])
        response = bus.recv(timeout=5)

        if response:
            log_message("Rx", response)
            print("WRITE_TPMS_FRONT: PASSED")
            return (True, front_mac.upper())  # success, written MAC
        else:
            print("No valid response for Front MAC Write.")
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
    # Example standalone test
    result = WRITE_TPMS_FRONT("C03687540000")
    print("Result:", result)
