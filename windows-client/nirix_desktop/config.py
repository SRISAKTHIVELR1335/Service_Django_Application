# nirix_desktop/config.py
"""
Created on Tue Dec  9 09:19:49 2025

@author: Sri.Sakthivel
"""

import os
import sys
import re
import json
import platform
from datetime import datetime
from typing import Dict, Any


def resource_path(relative_path: str) -> str:
    """
    Get absolute path to a resource.
    Works for dev and PyInstaller builds.
    """
    if getattr(sys, "frozen", False):
        base_path = sys._MEIPASS  # type: ignore[attr-defined]
    else:
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    return os.path.join(base_path, relative_path)


# -------------------------------------------------------------------
# Paths
# -------------------------------------------------------------------

# Folders (relative to windows-client root by default)
TEST_FOLDER = resource_path("Test_Programs")
ASSETS_FOLDER = resource_path("Vehicle_Images")

# Log folder – make sure it is writable on Windows
# You can change this to whatever you like (e.g. under %LOCALAPPDATA%)
LOG_FOLDER = resource_path("Test_Logs")
os.makedirs(LOG_FOLDER, exist_ok=True)

# Configuration JSON
CONFIG_PATH = resource_path("config.json")

# Approver email (kept same as original code)
APPROVER_EMAIL = "sri.sakthivel@tvsmotor.com"


def sanitize_for_filename(s: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", s or "").strip("._")


SESSION_TS = datetime.now().strftime("%Y.%m.%d_%H.%M.%S")
HOST_TAG = sanitize_for_filename(platform.node() or os.getenv("COMPUTERNAME", "host"))
LOG_BASENAME = f"{SESSION_TS}_NIRIX_{HOST_TAG}_{os.getpid()}"
LOG_FILE_PATH = os.path.join(LOG_FOLDER, f"{LOG_BASENAME}.log")  # for reference / future use


# -------------------------------------------------------------------
# Runtime configuration (from config.json)
# -------------------------------------------------------------------

# Defaults
CAN_INTERFACE = "PCAN_USBBUS1"
CAN_BITRATE = 500000
STRICT_SEQUENTIAL = True
THEME = "light"
ON_CLICK = "single"  # "single" or "double"
CONFIG: Dict[str, Any] = {}


def load_config() -> None:
    """
    Load config.json into CONFIG and update global variables.
    If file is missing or invalid, defaults are used and written back out.
    """
    global CAN_INTERFACE, CAN_BITRATE, STRICT_SEQUENTIAL, THEME, ON_CLICK, CONFIG

    CONFIG.clear()
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            raise ValueError("config.json root must be a JSON object.")
        CONFIG.update(data)
    except (FileNotFoundError, json.JSONDecodeError, ValueError):
        # Use defaults and write them out
        CONFIG.update(
            {
                "can_interface": CAN_INTERFACE,
                "can_bitrate": CAN_BITRATE,
                "strict_sequential": STRICT_SEQUENTIAL,
                "theme": THEME,
                "on_click": ON_CLICK,
                # SMTP optional section for RPi / Linux
                "smtp": {
                    "server": "smtp.office365.com",
                    "port": 587,
                    "use_tls": True,
                    "username": "sri.sakthivel@tvsmotor.com",
                    "password": "journey@123#",
                    "from_addr": "sri.sakthivel@tvsmotor.com",
                },
                "keep_log_days": 7,
            }
        )
        save_config()
        return

    # Populate globals
    CAN_INTERFACE = CONFIG.get("can_interface", CAN_INTERFACE)
    CAN_BITRATE = CONFIG.get("can_bitrate", CAN_BITRATE)
    STRICT_SEQUENTIAL = CONFIG.get("strict_sequential", STRICT_SEQUENTIAL)
    THEME = CONFIG.get("theme", THEME)
    ON_CLICK = CONFIG.get("on_click", ON_CLICK)


def save_config() -> None:
    """
    Persist current CONFIG dict to config.json.
    """
    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(CONFIG, f, indent=4)


# Initialize CONFIG at import
load_config()
