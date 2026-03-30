# -*- coding: utf-8 -*-
"""
NIRIX Desktop Diagnostic Client

Originally created for Raspberry Pi; this version is adapted for
Windows desktop with MySQL-based user storage instead of Excel.

Author: Sri.Sakthivel
"""

import sys
import os
import re
import json
import can
import importlib
import logging
import platform
import contextlib
import random
from datetime import datetime
from dataclasses import dataclass
from functools import partial
from typing import Optional, List, Tuple, Any

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QLineEdit, QMessageBox, QTextEdit, QStackedWidget, QFileDialog, QSizePolicy, QFrame,
    QScrollArea, QGridLayout, QProgressBar, QFormLayout, QComboBox, QInputDialog, QDialog
)
from PyQt5.QtGui import QPixmap, QFont, QIcon, QRegExpValidator
from PyQt5.QtCore import Qt, QRunnable, QThreadPool, pyqtSignal, QObject, QTimer, QSignalBlocker, QRegExp, QEvent

# -------------------------------------------------------------------
# Local package imports
# -------------------------------------------------------------------

from . import config as app_config
from . import db as db_layer
from . import models as model_defs
from .log_cleanup import cleanup_old_logs

# Short aliases to keep rest of code simple
TEST_FOLDER = app_config.TEST_FOLDER
ASSETS_FOLDER = app_config.ASSETS_FOLDER
LOG_FOLDER = app_config.LOG_FOLDER
CONFIG_PATH = app_config.CONFIG_PATH
APPROVER_EMAIL = app_config.APPROVER_EMAIL
LOG_BASENAME = app_config.LOG_BASENAME

CAN_INTERFACE = app_config.CAN_INTERFACE
CAN_BITRATE = app_config.CAN_BITRATE
STRICT_SEQUENTIAL = app_config.STRICT_SEQUENTIAL
THEME = app_config.THEME
ON_CLICK = app_config.ON_CLICK
config = app_config.CONFIG

# Module logger; GUI will show messages via QtLogHandler
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


# ---------------------------
# Configuration & Styles
# ---------------------------

def get_styles(theme: str = THEME):
    base_styles = {
        "HEADING": "color: #134686; font-size: 20px; font-weight: bold;",
        "BUTTON_PRIMARY": """
            QPushButton {
                background-color: #134686; color: white; border: none; padding: 10px;
                border-radius: 10px; font-size: 14px; font-weight: bold;
            }
            QPushButton:hover { background-color: #0f3e5e; }
            QPushButton:pressed { background-color: #0a2b45; }
            QPushButton:disabled { background-color: gray; color: darkgray; }
        """,
        "BUTTON_SECONDARY": """
            QPushButton {
                background-color: #134686; color: white; border: none; padding: 8px;
                border-radius: 5px;
            }
            QPushButton:hover { background-color: #0f3e5e; }
        """,
        "INPUT": """
            font-size: 14px; padding: 10px; border: 2px solid #ccc; border-radius: 10px;
            background-color: white;
        """,
        "HEADER_BAR": "background-color: #143B68; border: none;",
        "HEADER_TITLE": "color: white; font-size: 22px; font-weight: 800; letter-spacing: 1px;",
        "HEADER_ACCENT": "background-color: #C9142D; border: none;",
        "FOOTER_BAR": "background-color: #143B68; border: none;",
        "FOOTER_TEXT": "color: white; font-size: 11px;",
        "MODEL_FRAME": """
            border: 1px solid #cbd5e1;
            border-radius: 12px;
            background-color: transparent;
        """,
        "MODEL_HIGHLIGHT": """
            border: 2px solid #3b82f6;
            border-radius: 12px;
            background-color: transparent;
        """,
        "CATEGORY_FRAME": """
            border: 1px solid #cbd5e1;
            border-radius: 12px;
            background-color: transparent;
            padding: 10px; text-align: center;
        """,
        "CATEGORY_SELECTED": """
            border: 2px solid #3b82f6;
            border-radius: 12px;
            background-color: transparent;
            padding: 10px; text-align: center;
        """,
        "LOG_TEXT": "border: 1px solid #ccc; border-radius: 10px;",
        "TEST_CARD": """
            border: 1px solid #cbd5e1;
            border-radius: 12px;
            background-color: transparent;
        """,
        "TEST_RESULT_IDLE": "color: gray; background-color: transparent; border: none;",
        "TEST_RESULT_RUNNING": "color: orange; background-color: transparent; border: none;",
        "TEST_RESULT_PASS": "color: green; background-color: transparent; border: none;",
        "TEST_RESULT_FAIL": "color: red; background-color: transparent; border: none;",
        "LOGIN_FRAME": """
            border-radius: 20px; background-color: #f0f8ff;
            padding: 20px; margin: 20px;
        """,
        "LOGIN_BUTTON": """
            QPushButton { background-color: #134686; color: white; border: none; padding: 12px;
                          border-radius: 10px; font-size: 16px; font-weight: bold; }
            QPushButton:hover { background-color: #0f3e5e; }
        """,
        "REG_BUTTON": """
            QPushButton { background-color: transparent; color: #134686; border: 1px solid #134686;
                          padding: 8px; border-radius: 5px; font-size: 14px; }
            QPushButton:hover { background-color: #134686; color: white; }
        """
    }

    if theme == "dark":
        dark_overrides = {
            "HEADING": "color: #4DA8DA; font-size: 20px; font-weight: bold;",
            "BUTTON_PRIMARY": """
                QPushButton {
                    background-color: #2C3E50; color: #ECF0F1; border: none; padding: 10px;
                    border-radius: 10px; font-size: 14px; font-weight: bold;
                }
                QPushButton:hover { background-color: #34495E; }
                QPushButton:pressed { background-color: #1B2631; }
                QPushButton:disabled { background-color: #7F8C8D; color: #BDC3C7; }
            """,
            "BUTTON_SECONDARY": """
                QPushButton {
                    background-color: #2C3E50; color: #ECF0F1; border: none; padding: 8px;
                    border-radius: 5px;
                }
                QPushButton:hover { background-color: #34495E; }
            """,
            "INPUT": """
                font-size: 14px; padding: 10px; border: 2px solid #7F8C8D; border-radius: 10px;
                background-color: #34495E; color: #ECF0F1;
            """,
            "HEADER_BAR": "background-color: #1B2631; border: none;",
            "HEADER_TITLE": "color: #ECF0F1; font-size: 22px; font-weight: 800; letter-spacing: 1px;",
            "HEADER_ACCENT": "background-color: #E74C3C; border: none;",
            "FOOTER_BAR": "background-color: #1B2631; border: none;",
            "FOOTER_TEXT": "color: #BDC3C7; font-size: 11px;",
            "MODEL_FRAME": """
                border: 1px solid #7F8C8D;
                border-radius: 12px;
                background-color: #2C3E50;
            """,
            "MODEL_HIGHLIGHT": """
                border: 2px solid #3498DB;
                border-radius: 12px;
                background-color: #2C3E50;
            """,
            "CATEGORY_FRAME": """
                border: 1px solid #7F8C8D;
                border-radius: 12px;
                background-color: #2C3E50;
                padding: 10px; text-align: center;
                color: #ECF0F1;
            """,
            "CATEGORY_SELECTED": """
                border: 2px solid #3498DB;
                border-radius: 12px;
                background-color: #2C3E50;
                padding: 10px; text-align: center;
                color: #ECF0F1;
            """,
            "LOG_TEXT": "border: 1px solid #7F8C8D; border-radius: 10px; background-color: #2C3E50; color: #ECF0F1;",
            "TEST_CARD": """
                border: 1px solid #7F8C8D;
                border-radius: 12px;
                background-color: #2C3E50;
            """,
            "TEST_RESULT_IDLE": "color: #BDC3C7; background-color: transparent; border: none;",
            "TEST_RESULT_RUNNING": "color: #F39C12; background-color: transparent; border: none;",
            "TEST_RESULT_PASS": "color: #27AE60; background-color: transparent; border: none;",
            "TEST_RESULT_FAIL": "color: #E74C3C; background-color: transparent; border: none;",
            "LOGIN_FRAME": """
                border: 2px solid #3498DB; border-radius: 20px; background-color: #34495E;
                padding: 20px; margin: 20px; color: #ECF0F1;
            """,
            "LOGIN_BUTTON": """
                QPushButton { background-color: #3498DB; color: #ECF0F1; border: none; padding: 12px;
                              border-radius: 10px; font-size: 16px; font-weight: bold; }
                QPushButton:hover { background-color: #2980B9; }
            """,
            "REG_BUTTON": """
                QPushButton { background-color: transparent; color: #3498DB; border: 1px solid #3498DB;
                              padding: 8px; border-radius: 5px; font-size: 14px; }
                QPushButton:hover { background-color: #3498DB; color: #ECF0F1; }
            """
        }
        base_styles.update(dark_overrides)

    return base_styles


STYLES = get_styles(THEME)

# Vehicle images & models from models.py
VEHICLE_IMAGES = model_defs.VEHICLE_IMAGES
VEHICLE_MODELS = model_defs.VEHICLE_MODELS


# ---------------------------
# Thread
# ---------------------------

class WorkerSignals(QObject):
    finished = pyqtSignal(object)
    error = pyqtSignal(tuple)


class Worker(QRunnable):
    def __init__(self, fn: callable, *args: Any, **kwargs: Any):
        super().__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

    def run(self):
        try:
            res = self.fn(*self.args, **self.kwargs)
            self.signals.finished.emit(res)
        except Exception as e:
            import traceback
            tb = traceback.format_exc()
            self.signals.error.emit((e, tb))


# ---------------------------
# Log bridge to GUI (prints + logging)
# ---------------------------

class LogEmitter(QObject):
    log = pyqtSignal(str, str)  # level, message


class QtLogHandler(logging.Handler):
    def __init__(self, emitter: LogEmitter):
        super().__init__()
        self._emitter = emitter

    def emit(self, record: logging.LogRecord) -> None:
        # Skip if explicitly marked as "skip_gui"
        if getattr(record, "skip_gui", False):
            return
        try:
            msg = self.format(record)
        except Exception:
            msg = record.getMessage()
        self._emitter.log.emit(record.levelname, msg)


class EmittingStream:
    """File-like object that sends writes to the GUI log via LogEmitter."""

    def __init__(self, emitter: LogEmitter, level: str = "INFO"):
        self._emitter = emitter
        self._level = level
        self._buf = ""

    def write(self, s: str) -> None:
        if not s:
            return
        self._buf += s
        while "\n" in self._buf:
            line, self._buf = self._buf.split("\n", 1)
            line = line.rstrip()
            if line:
                self._emitter.log.emit(self._level, line)

    def flush(self) -> None:
        if self._buf:
            self._emitter.log.emit(self._level, self._buf.rstrip())
            self._buf = ""


# ---------------------------
# Utilities
# ---------------------------

def import_callable_from_dir(base_dir: str, module_name: str, func_name: str) -> callable:
    import importlib.util

    if not base_dir or not os.path.isdir(base_dir):
        raise ImportError(f"Base directory not found: {base_dir}")

    candidate = os.path.join(base_dir, f"{module_name}.py")
    if not os.path.exists(candidate):
        raise ImportError(f"Module file not found: {candidate}")

    unique_modname = f"{os.path.basename(base_dir)}.{module_name}"
    spec = importlib.util.spec_from_file_location(unique_modname, candidate)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore[arg-type]

    if not hasattr(mod, func_name):
        raise AttributeError(f"Module '{module_name}' in {base_dir} has no attribute '{func_name}'")

    return getattr(mod, func_name)


def parse_mac_input(text: str) -> bytes:
    text = text.strip().upper()
    if not text:
        raise ValueError("No MAC input provided")
    if not re.match(r'^[0-9A-F]{12}$', text):
        raise ValueError("MAC must be 12 hex characters (e.g., AABBCCDDEEFF)")
    return bytes.fromhex(text)


def check_can_connection() -> bool:
    """
    Check CAN connection for the selected interface.
    PCAN:      channel='PCAN_USBBUS1', bustype='pcan'
    SocketCAN: channel='can0', bustype='socketcan'
    """
    try:
        iface = str(CAN_INTERFACE)
        if iface.upper().startswith("PCAN"):
            bus = can.interface.Bus(channel=iface, bustype="pcan", bitrate=CAN_BITRATE, fd=False)
        elif iface.startswith("can"):
            # For socketcan, bitrate is usually set via 'ip link' at OS level
            bus = can.interface.Bus(channel=iface, bustype="socketcan")
        else:
            logger.error(f"Unknown CAN interface '{iface}' for connection check.")
            return False
        bus.shutdown()
        return True
    except Exception as e:
        logger.error(f"CAN connection check failed for {CAN_INTERFACE}: {e}")
        return False


# VIN wildcard-aware match: X matches any character (both in pattern and typed)
def vin_matches(pattern: str, typed: str) -> bool:
    pat = pattern.strip().upper()
    t = typed.strip().upper()
    for i in range(min(len(pat), len(t))):
        pc = pat[i]
        tc = t[i]
        if pc != 'X' and tc != 'X' and pc != tc:
            return False
    return True


# ---------------------------
# Data classes
# ---------------------------

@dataclass
class TestRow:
    module: str
    func: str
    mac_input: Optional[QLineEdit]
    btn: QPushButton
    result: QLabel
    actual: Optional[QLabel] = None  # shows actual value (e.g., MAC)


# ---------------------------
# Small helper widgets
# ---------------------------

class ApprovalCodeDialog(QDialog):
    """Custom dialog for entering and resending approver code."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Approval Code")
        self.setModal(True)

        layout = QVBoxLayout(self)

        label = QLabel("Enter the 6-digit approval code shared by the approver:")
        layout.addWidget(label)

        self.code_edit = QLineEdit()
        self.code_edit.setMaxLength(6)
        self.code_edit.setPlaceholderText("e.g. 123456")
        self.code_edit.setValidator(QRegExpValidator(QRegExp("[0-9]{0,6}"), self.code_edit))
        self.code_edit.setStyleSheet(STYLES["INPUT"])
        layout.addWidget(self.code_edit)

        btn_row = QHBoxLayout()
        self.verify_btn = QPushButton("VERIFY")
        self.verify_btn.setStyleSheet(STYLES["LOGIN_BUTTON"])

        self.resend_btn = QPushButton("RESEND CODE")
        self.resend_btn.setStyleSheet(STYLES["REG_BUTTON"])

        self.cancel_btn = QPushButton("CANCEL")
        self.cancel_btn.setStyleSheet(STYLES["REG_BUTTON"])

        btn_row.addWidget(self.verify_btn)
        btn_row.addWidget(self.resend_btn)
        btn_row.addWidget(self.cancel_btn)
        layout.addLayout(btn_row)

        self.verify_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)
        # resend_btn is connected from MainWindow


# ---------------------------
# MainWindow
# ---------------------------

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NIRIX DIAGNOSTIC TOOL")
        self.setMinimumSize(720, 1250)

        self.threadpool = QThreadPool()
        self.threadpool.setMaxThreadCount(4)
        self.test_fn_cache: dict = {}

        self.selected_vehicle: Optional[str] = None
        self.current_filter: str = "ALL MODELS"
        self.search_text: str = ""
        self.vin_filter_text: str = ""
        self.filtered_models_cache: List[Tuple[str, str, str, str]] = []
        self.vin_input: Optional[QLineEdit] = None

        self.test_queue: List[str] = []
        self.run_all_progress: Optional[QProgressBar] = None
        self.current_category_frame: Optional[QFrame] = None

        self.full_log = None
        self.quick_log = None
        self.suppress_vin_change = False
        self._logs_return_to = None

        self.user_name: Optional[str] = None  # Logged in user
        self.user_empid: Optional[str] = None
        self.user_email: Optional[str] = None

        # Active model deployment
        self.active_model: Optional[str] = None
        self.active_model_dir: Optional[str] = None

        # Run All state
        self.run_all_mode: Optional[str] = None  # 'strict' or 'parallel'
        self.run_all_stopped: bool = False
        self.completed_tests: int = 0
        self.pending_tests: int = 0

        # Tests page dynamic container refs
        self.tests_container_layout: Optional[QVBoxLayout] = None
        self.test_rows: dict = {}
        self.tests_scroll: Optional[QScrollArea] = None

        # TPMS MACs (session)
        self.tpms_macs = {"front": None, "rear": None}

        # Pending registration state
        self._pending_registration = None  # dict with name, empid, email, approver, pin, approval_code
        self.reg_submit_btn: Optional[QPushButton] = None

        # Log cleanup
        try:
            keep_days = int(config.get("keep_log_days", 7))
        except Exception:
            keep_days = 7
        try:
            cleanup_old_logs(LOG_FOLDER, keep_days=keep_days)
            logger.info("Log cleanup completed successfully.")
        except Exception as e:
            logger.warning(f"Error executing log cleanup: {e}")

        # Build pages
        self.stack = QStackedWidget()
        self.login_page = self.build_login_page()
        self.dashboard = self.build_dashboard_page()
        self.tests_page = self.build_tests_page()
        self.log_page = self.build_log_page()
        self.registration_page = self.build_registration_page()

        # Add pages to stack
        self.stack.addWidget(self.login_page)       # 0
        self.stack.addWidget(self.dashboard)        # 1
        self.stack.addWidget(self.tests_page)       # 2
        self.stack.addWidget(self.log_page)         # 3
        self.stack.addWidget(self.registration_page)  # 4

        # Wrap with header and footer
        shell = QWidget()
        shell_layout = QVBoxLayout(shell)
        shell_layout.setContentsMargins(0, 0, 0, 0)
        shell_layout.setSpacing(0)
        shell_layout.addWidget(self._build_header_bar())
        shell_layout.addWidget(self.stack, 1)
        shell_layout.addWidget(self._build_footer_bar())
        self.setCentralWidget(shell)

        # Apply theme to app
        app.setStyleSheet(self._get_app_stylesheet())

        # Log bridge: forward python logging and prints to GUI preview
        self._log_emitter = LogEmitter()
        self._log_emitter.log.connect(lambda level, msg: self.append_log(msg, level))

        self._qt_log_handler = QtLogHandler(self._log_emitter)
        self._qt_log_handler.setLevel(logging.DEBUG)

        # Attach Qt handler to root logger and remove any other handlers (no console/file)
        root_logger = logging.getLogger()
        for h in list(root_logger.handlers):
            root_logger.removeHandler(h)
        root_logger.addHandler(self._qt_log_handler)
        root_logger.setLevel(logging.DEBUG)

        # Redirect global stdout/stderr so print() also goes only to GUI log
        sys.stdout = EmittingStream(self._log_emitter, level="INFO")
        sys.stderr = EmittingStream(self._log_emitter, level="ERROR")

        # Log views
        self.full_log = self.log_page.findChild(QTextEdit)
        self.quick_log = self.dashboard.findChild(QTextEdit, "quick_log")

    def _get_app_stylesheet(self):
        if THEME == "dark":
            return """
                QMainWindow { background-color: #1B2631; color: #ECF0F1; }
                QWidget { background-color: #1B2631; color: #ECF0F1; }
                QLabel { color: #ECF0F1; }
                QLineEdit { background-color: #34495E; color: #ECF0F1; border: 2px solid #7F8C8D; border-radius: 10px; padding: 10px; font-size: 14px; }
                QTextEdit { background-color: #2C3E50; color: #ECF0F1; border: 1px solid #7F8C8D; border-radius: 10px; }
                QScrollArea { background-color: #1B2631; }
                QProgressBar { background-color: #34495E; border: 1px solid #7F8C8D; border-radius: 5px; text-align: center; color: #ECF0F1; }
                QProgressBar::chunk { background-color: #3498DB; }
                QDialog { background-color: #2C3E50; color: #ECF0F1; }
            """
        else:
            return """
                QMainWindow { background-color: #F8F9FA; color: #134686; }
                QWidget { background-color: #F8F9FA; color: #134686; }
                QLabel { color: #134686; }
                QLineEdit { background-color: white; color: #134686; border: 2px solid #ccc; border-radius: 10px; padding: 10px; font-size: 14px; }
                QTextEdit { background-color: white; color: #134686; border: 1px solid #ccc; border-radius: 10px; }
                QScrollArea { background-color: #F8F9FA; }
                QProgressBar { background-color: #E9ECEF; border: 1px solid #ccc; border-radius: 5px; text-align: center; color: #134686; }
                QProgressBar::chunk { background-color: #007BFF; }
                QDialog { background-color: white; color: #134686; }
            """

    def _build_header_bar(self) -> QWidget:
        header_wrap = QWidget()
        v = QVBoxLayout(header_wrap)
        v.setContentsMargins(0, 0, 0, 0)
        v.setSpacing(0)

        bar = QFrame()
        bar.setStyleSheet(STYLES["HEADER_BAR"])
        h = QHBoxLayout(bar)
        h.setContentsMargins(16, 10, 16, 10)
        h.setSpacing(8)

        left_logo = QLabel()
        left_logo.setFixedWidth(120)
        left_logo.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        left_logo.setStyleSheet("border: none; background: transparent;")
        left_logo_path = os.path.join(ASSETS_FOLDER, "Nirix_Name_Logo.png")
        if os.path.exists(left_logo_path):
            pix_left = QPixmap(left_logo_path).scaled(150, 40, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            left_logo.setPixmap(pix_left)
        else:
            left_logo.setText("TVS NIRIX")
            left_logo.setStyleSheet("color: white; font-weight: 600; border: none; background: transparent;")

        center_spacer = QLabel()
        center_spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        right_logo = QLabel()
        right_logo.setFixedWidth(120)
        right_logo.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        right_logo.setStyleSheet("border: none; background: transparent;")
        right_logo_path = os.path.join(ASSETS_FOLDER, "TVS_Logo_White.png")
        if os.path.exists(right_logo_path):
            pix_right = QPixmap(right_logo_path).scaled(110, 30, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            right_logo.setPixmap(pix_right)
        else:
            right_logo.setText("TVS")
            right_logo.setStyleSheet("color: white; font-weight: 800; border: none; background: transparent;")

        h.addWidget(left_logo)
        h.addWidget(center_spacer, 1)
        h.addWidget(right_logo)

        accent = QFrame()
        accent.setFixedHeight(4)
        accent.setStyleSheet(STYLES["HEADER_ACCENT"])

        v.addWidget(bar)
        v.addWidget(accent)
        return header_wrap

    def _build_footer_bar(self) -> QWidget:
        footer = QFrame()
        footer.setStyleSheet(STYLES["FOOTER_BAR"])
        h = QHBoxLayout(footer)
        h.setContentsMargins(16, 6, 16, 6)
        h.setSpacing(0)
        year = datetime.now().year
        foot_lbl = QLabel(f"{year} PED@CT&T. All rights reserved.")
        foot_lbl.setStyleSheet(STYLES["FOOTER_TEXT"])
        foot_lbl.setAlignment(Qt.AlignCenter)
        h.addStretch()
        h.addWidget(foot_lbl)
        h.addStretch()
        return footer

    # ---------------------------
    # Helpers for forcing case
    # ---------------------------

    def _enforce_upper(self, widget: QLineEdit, text: str) -> None:
        """Force QLineEdit text to UPPERCASE while keeping cursor position."""
        up = text.upper()
        if text != up:
            pos = widget.cursorPosition()
            with QSignalBlocker(widget):
                widget.setText(up)
            widget.setCursorPosition(pos)

    def _enforce_lower(self, widget: QLineEdit, text: str) -> None:
        """Force QLineEdit text to lowercase while keeping cursor position."""
        low = text.lower()
        if text != low:
            pos = widget.cursorPosition()
            with QSignalBlocker(widget):
                widget.setText(low)
            widget.setCursorPosition(pos)

    # ---------------------------
    # Login Page (with VCI dropdown) + link to Registration Page
    # ---------------------------

    def build_login_page(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setSpacing(20)
        layout.setContentsMargins(40, 40, 40, 40)

        title = QLabel("Welcome, NIRIX Diagnostics")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Arial", 24, QFont.Bold))
        title.setStyleSheet("color: #134686; margin-bottom: 20px;")
        layout.addWidget(title)

        # Logo card
        logo_frame = QFrame()
        logo_frame.setStyleSheet(STYLES["LOGIN_FRAME"])
        logo_layout = QVBoxLayout(logo_frame)

        tvs_logo = QLabel()
        tvs_logo.setAlignment(Qt.AlignCenter)
        tvs_path = os.path.join(ASSETS_FOLDER, "Nirix_Logo.png")
        if os.path.exists(tvs_path):
            pix = QPixmap(tvs_path).scaled(300, 350, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            tvs_logo.setPixmap(pix)
        else:
            tvs_logo.setText("TVS")
            tvs_logo.setFont(QFont("Arial", 48, QFont.Bold))
            tvs_logo.setStyleSheet("color: #134686;")

        logo_layout.addWidget(tvs_logo)
        layout.addWidget(logo_frame, alignment=Qt.AlignCenter)

        # Login Form
        form_layout = QFormLayout()
        self.login_email = QLineEdit()
        self.login_email.setPlaceholderText("Enter your email ID")
        self.login_email.setStyleSheet(STYLES["INPUT"])

        # 4-digit PIN instead of password
        self.login_password = QLineEdit()
        self.login_password.setPlaceholderText("Enter 4-digit PIN")
        self.login_password.setEchoMode(QLineEdit.Password)
        self.login_password.setStyleSheet(STYLES["INPUT"])
        self.login_password.setMaxLength(4)
        pin_regex = QRegExp("[0-9]{0,4}")
        self.login_password.setValidator(QRegExpValidator(pin_regex, self.login_password))

        # VCI as dropdown (PCAN / SocketCAN - MCP25919)
        self.login_vci = QComboBox()
        self.login_vci.setStyleSheet(STYLES["INPUT"])
        self.login_vci.addItem("PCAN", "pcan")
        self.login_vci.addItem("SocketCAN - MCP2515", "socketcan")
        # Pre-select based on current CAN_INTERFACE from config
        if str(CAN_INTERFACE).upper().startswith("PCAN"):
            self.login_vci.setCurrentIndex(0)
        else:
            self.login_vci.setCurrentIndex(1)

        form_layout.addRow("Email ID:", self.login_email)
        form_layout.addRow("PIN:", self.login_password)
        form_layout.addRow("VCI:", self.login_vci)

        login_widget = QWidget()
        login_widget.setLayout(form_layout)
        layout.addWidget(login_widget)

        # Proceed button
        proceed_btn = QPushButton("PROCEED")
        proceed_btn.setStyleSheet(STYLES["LOGIN_BUTTON"])
        proceed_btn.clicked.connect(self.on_proceed_login)
        layout.addWidget(proceed_btn, alignment=Qt.AlignCenter)

        # Registration info + button
        reg_text = QLabel("Not yet registered? Please go through the registration process")
        reg_text.setAlignment(Qt.AlignCenter)
        reg_text.setStyleSheet("color: gray; font-size: 12px;")
        layout.addWidget(reg_text)

        reg_btn = QPushButton("REGISTRATION")
        reg_btn.setStyleSheet(STYLES["REG_BUTTON"])
        reg_btn.clicked.connect(self.show_registration_page)
        layout.addWidget(reg_btn, alignment=Qt.AlignCenter)

        return w

    # ---------------------------
    # Registration Page (separate screen)
    # ---------------------------

    def build_registration_page(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)

        # Title at top-left
        title = QLabel("REGISTRATION")
        title.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        title.setFont(QFont("Arial", 24, QFont.Bold))
        title.setStyleSheet("color: #134686; margin-bottom: 10px;")
        layout.addWidget(title)

        # Card frame for the form
        form_frame = QFrame()
        form_frame.setStyleSheet(STYLES["LOGIN_FRAME"])
        form_layout = QFormLayout(form_frame)

        # Inputs
        self.reg_name_input = QLineEdit()
        self.reg_empid_input = QLineEdit()
        self.reg_email_input = QLineEdit()
        # Approver not visible on UI, use fixed APPROVER_EMAIL instead
        self.reg_pin_input = QLineEdit()
        self.reg_pin_confirm_input = QLineEdit()

        # PIN fields: 4-digit numeric, masked
        for pin_edit in (self.reg_pin_input, self.reg_pin_confirm_input):
            pin_edit.setEchoMode(QLineEdit.Password)
            pin_edit.setMaxLength(4)
            pin_regex = QRegExp("[0-9]{0,4}")
            pin_edit.setValidator(QRegExpValidator(pin_regex, pin_edit))

        self.reg_name_input.setPlaceholderText("Enter your name")
        self.reg_empid_input.setPlaceholderText("Enter your Employee ID")
        self.reg_email_input.setPlaceholderText("Enter your email ID")
        self.reg_pin_input.setPlaceholderText("Enter 4-digit PIN")
        self.reg_pin_confirm_input.setPlaceholderText("Re-enter 4-digit PIN")

        # Force UPPERCASE for Name
        self.reg_name_input.textChanged.connect(
            lambda text: self._enforce_upper(self.reg_name_input, text)
        )

        # Employee ID: digits only
        empid_regex = QRegExp("[0-9]{0,20}")
        self.reg_empid_input.setValidator(QRegExpValidator(empid_regex, self.reg_empid_input))

        # Force lowercase for Email
        self.reg_email_input.textChanged.connect(
            lambda text: self._enforce_lower(self.reg_email_input, text)
        )

        # Bigger width for entry fields
        for edit in (
            self.reg_name_input,
            self.reg_empid_input,
            self.reg_email_input,
            self.reg_pin_input,
            self.reg_pin_confirm_input,
        ):
            edit.setStyleSheet(STYLES["INPUT"])
            edit.setMinimumWidth(400)

        form_layout.addRow("Name:", self.reg_name_input)
        form_layout.addRow("Employee ID:", self.reg_empid_input)
        form_layout.addRow("Email ID:", self.reg_email_input)
        # Approver row removed from UI
        form_layout.addRow("PIN:", self.reg_pin_input)
        form_layout.addRow("Confirm PIN:", self.reg_pin_confirm_input)

        # Buttons
        btns_layout = QHBoxLayout()

        self.reg_submit_btn = QPushButton("REGISTER")
        self.reg_submit_btn.setStyleSheet(STYLES["LOGIN_BUTTON"])
        self.reg_submit_btn.clicked.connect(self.handle_registration)

        reg_cancel_btn = QPushButton("BACK")
        reg_cancel_btn.setStyleSheet(STYLES["REG_BUTTON"])
        reg_cancel_btn.clicked.connect(lambda: self.stack.setCurrentWidget(self.login_page))

        btns_layout.addWidget(self.reg_submit_btn)
        btns_layout.addWidget(reg_cancel_btn)
        form_layout.addRow(btns_layout)

        layout.addWidget(form_frame, alignment=Qt.AlignHCenter | Qt.AlignTop)
        return w

    def show_registration_page(self):
        self.stack.setCurrentWidget(self.registration_page)

    # ---------------------------
    # DB-backed "secure excel" helpers
    # ---------------------------

    def _load_secure_excel_data(self) -> List[List[Any]]:
        """
        Replaced by DB:

        Returns rows as [Name, EmpID, Email, Approver, PIN]
        where Approver is blank and PIN is masked ("****").
        """
        try:
            rows = db_layer.get_all_users_for_ui()
            self.append_log("Loaded users from DB (replacing Excel).", "INFO")
            return rows
        except Exception as e:
            self.append_log(f"DB read failed: {e}", "ERROR")
            return []

    def _save_secure_excel_data(self, new_row: List[Any]) -> None:
        """
        Replaced by DB:

        new_row: [Name, EmpID, Email, Approver, PIN]
        Only Name, EmpID, Email, PIN are stored in MySQL.
        """
        name = str(new_row[0]).strip()
        empid = str(new_row[1]).strip()
        email = str(new_row[2]).strip().lower()
        pin = str(new_row[4]).strip()

        if not (name and empid and email and pin):
            raise ValueError("Name, Employee ID, Email, and PIN are required.")

        try:
            db_layer.create_user(name, empid, email, pin)
            self.append_log(f"User created in DB: {email}", "INFO")
        except Exception as e:
            self.append_log(f"DB write failed: {e}", "ERROR")
            raise

    # ---------------------------
    # Email sending (same as original)
    # ---------------------------

    def send_approval_email(self, approver_email: str,
                            user_name: str, empid: str, user_email: str,
                            code: str) -> None:
        """
        Cross-platform approval email:
          - Windows: send via Outlook COM (pywin32)
          - Raspberry Pi / Linux / macOS: send via SMTP (config.json)

        Raises on error so handle_registration() can show a message box.
        """

        subject = "Approval Required for New NIRIX Registration"
        body = (
            "Dear Approver,\n\n"
            "A new user has requested access to the NIRIX Diagnostic Tool.\n\n"
            f"Name        : {user_name}\n"
            f"Employee ID : {empid}\n"
            f"Email ID    : {user_email}\n\n"
            f"Approval Code: {code}\n\n"
            "Please share this code with the user (email/Teams/Phone) so they "
            "can complete the registration.\n\n"
            "Regards,\n"
            "NIRIX Diagnostic Tool\n"
        )

        system_name = platform.system().lower()

        # ------------------------------------------------
        # 1) WINDOWS → OUTLOOK (YOUR EXISTING METHOD)
        # ------------------------------------------------
        if system_name == "windows":
            try:
                import win32com.client as win32  # pywin32 required on Windows

                outlook = win32.Dispatch("Outlook.Application")
                mail = outlook.CreateItem(0)
                mail.To = approver_email
                mail.Subject = subject
                mail.Body = body
                mail.Send()

                self.append_log(
                    f"Approval email sent to {approver_email} via Outlook (Windows).",
                    "INFO",
                )
                return
            except Exception as e:
                # If Outlook fails, fall back to SMTP for robustness
                self.append_log(
                    f"Windows Outlook sending failed, falling back to SMTP: {e}",
                    "WARNING",
                )

        # ------------------------------------------------
        # 2) RPi / Linux / macOS → SMTP SENDING
        # ------------------------------------------------
        smtp_cfg = config.get("smtp", {})
        server = smtp_cfg.get("server")
        port = smtp_cfg.get("port", 587)
        use_tls = smtp_cfg.get("use_tls", True)
        username = smtp_cfg.get("username")
        password = smtp_cfg.get("password")
        from_addr = smtp_cfg.get("from_addr") or username

        # Validate config
        if not (server and username and password and from_addr):
            raise RuntimeError(
                "SMTP configuration is missing or incomplete in config.json.\n"
                "Required fields: server, username, password, from_addr"
            )

        try:
            import smtplib
            from email.message import EmailMessage

            msg = EmailMessage()
            msg["Subject"] = subject
            msg["From"] = from_addr
            msg["To"] = approver_email
            msg.set_content(body)

            with smtplib.SMTP(server, port, timeout=20) as smtp:
                if use_tls:
                    smtp.starttls()
                smtp.login(username, password)
                smtp.send_message(msg)

            self.append_log(
                f"Approval email sent to {approver_email} via SMTP ({server}:{port}).",
                "INFO",
            )

        except Exception as e:
            self.append_log(f"Failed to send approval email via SMTP: {e}", "ERROR")
            raise

    # ---------------------------
    # Registration flow with async email + resend
    # ---------------------------

    def handle_registration(self):
        """Handle registration on the separate registration page with approval flow (async email + resend)."""
        name = self.reg_name_input.text().strip()
        empid = self.reg_empid_input.text().strip()
        email = self.reg_email_input.text().strip().lower()
        approver = APPROVER_EMAIL  # fixed approver, not shown on UI
        pin = self.reg_pin_input.text().strip()
        pin_confirm = self.reg_pin_confirm_input.text().strip()

        if not all([name, empid, email, approver, pin, pin_confirm]):
            QMessageBox.warning(self, "Registration Error", "All fields are required.")
            return

        # Validate 4-digit PIN
        if not re.fullmatch(r"\d{4}", pin):
            QMessageBox.warning(self, "Registration Error", "PIN must be exactly 4 digits.")
            return

        if pin != pin_confirm:
            QMessageBox.warning(self, "Registration Error", "PIN and Confirm PIN do not match.")
            return

        # STEP 1: Generate a 6-digit approval code and store pending registration
        approval_code = f"{random.randint(0, 999999):06d}"
        self.append_log(f"Generated approval code {approval_code} for {email}", "DEBUG")

        self._pending_registration = {
            "name": name,
            "empid": empid,
            "email": email,
            "approver": approver,
            "pin": pin,
            "approval_code": approval_code,
        }

        # Disable REGISTER button while sending email
        if self.reg_submit_btn:
            self.reg_submit_btn.setEnabled(False)

        # STEP 2: Send email asynchronously so UI doesn't freeze
        worker = Worker(
            self.send_approval_email,
            approver,
            name,
            empid,
            email,
            approval_code
        )
        worker.signals.finished.connect(self._on_initial_approval_email_sent)
        worker.signals.error.connect(self._on_initial_approval_email_error)
        self.threadpool.start(worker)

        QMessageBox.information(
            self,
            "Sending Email",
            "Sending approval email to the approver.\n\n"
            "Please wait for the Approver Code dialog to appear."
        )

    def _on_initial_approval_email_sent(self, _result):
        # Re-enable REGISTER button
        if self.reg_submit_btn:
            self.reg_submit_btn.setEnabled(True)

        self.append_log("Approval email sent successfully.", "INFO")
        self._show_approval_code_dialog()

    def _on_initial_approval_email_error(self, errtb):
        if self.reg_submit_btn:
            self.reg_submit_btn.setEnabled(True)

        err, tb = errtb
        self.append_log(f"Failed to send approval email: {err}", "ERROR")
        self.append_log(tb, "DEBUG")
        QMessageBox.warning(
            self,
            "Registration Error",
            f"Failed to send approval email.\n\nDetails: {err}",
        )
        self._pending_registration = None

    def _show_approval_code_dialog(self):
        if not self._pending_registration:
            return

        dlg = ApprovalCodeDialog(self)

        # Wire up RESEND CODE button
        dlg.resend_btn.clicked.connect(lambda: self._resend_approval_code(dlg))

        while True:
            result = dlg.exec_()
            if result != QDialog.Accepted:
                QMessageBox.information(
                    self,
                    "Registration",
                    "Registration cancelled (approval code not entered).",
                )
                self._pending_registration = None
                return

            entered_code = dlg.code_edit.text().strip()
            expected_code = self._pending_registration.get("approval_code", "")

            if entered_code != expected_code:
                QMessageBox.warning(self, "Registration Error", "Invalid approval code. Please try again.")
                continue  # reopen dialog

            # Code is correct: finalize registration
            break

        reg = self._pending_registration
        try:
            # Save to DB as [Name, EmpID, Email, Approver, PIN]
            self._save_secure_excel_data(
                [reg["name"], reg["empid"], reg["email"], reg["approver"], reg["pin"]]
            )

            QMessageBox.information(self, "Success", "Registration successful!")

            # Pre-fill login email and clear PIN
            self.login_email.setText(reg["email"])
            self.login_password.clear()

            # Clear registration fields
            self.reg_name_input.clear()
            self.reg_empid_input.clear()
            self.reg_email_input.clear()
            self.reg_pin_input.clear()
            self.reg_pin_confirm_input.clear()

            # Go back to login page
            self.stack.setCurrentWidget(self.login_page)
        except ValueError as ve:
            QMessageBox.warning(self, "Registration Error", str(ve))
        except Exception as e:
            QMessageBox.warning(self, "Registration Error", f"Failed to register: {e}")
        finally:
            self._pending_registration = None

    def _resend_approval_code(self, dialog: ApprovalCodeDialog):
        """Generate a new code and resend email for the same pending user."""
        if not self._pending_registration:
            return

        # New 6-digit code
        new_code = f"{random.randint(0, 999999):06d}"
        self._pending_registration["approval_code"] = new_code
        self.append_log(f"Resending approval code {new_code} to {self._pending_registration['email']}", "DEBUG")

        dialog.resend_btn.setEnabled(False)

        worker = Worker(
            self.send_approval_email,
            self._pending_registration["approver"],
            self._pending_registration["name"],
            self._pending_registration["empid"],
            self._pending_registration["email"],
            new_code,
        )

        def on_resend_done(_):
            dialog.resend_btn.setEnabled(True)
            QMessageBox.information(self, "Resent", "Approval code resent to the approver.")

        def on_resend_error(errtb):
            err, tb = errtb
            dialog.resend_btn.setEnabled(True)
            self.append_log(f"Failed to resend approval email: {err}", "ERROR")
            self.append_log(tb, "DEBUG")
            QMessageBox.warning(
                self,
                "Resend Error",
                f"Failed to resend approval email.\n\nDetails: {err}",
            )

        worker.signals.finished.connect(on_resend_done)
        worker.signals.error.connect(on_resend_error)
        self.threadpool.start(worker)

    def _apply_vci_selection(self, vci_mode: str):
        """Set CAN_INTERFACE / CAN_BITRATE based on selected VCI and update config.json."""
        global CAN_INTERFACE, CAN_BITRATE, config

        if vci_mode == "pcan":
            CAN_INTERFACE = "PCAN_USBBUS1"
            CAN_BITRATE = 500000
        elif vci_mode == "socketcan":
            CAN_INTERFACE = "can0"
            CAN_BITRATE = 500000
        else:
            self.append_log(f"Unknown VCI selection '{vci_mode}'. Defaulting to PCAN.", "WARNING")
            CAN_INTERFACE = "PCAN_USBBUS1"
            CAN_BITRATE = 500000

        config["can_interface"] = CAN_INTERFACE
        config["can_bitrate"] = CAN_BITRATE

        try:
            with open(CONFIG_PATH, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=4)
            self.append_log(
                f"Updated CAN config: interface={CAN_INTERFACE}, bitrate={CAN_BITRATE} in {CONFIG_PATH}",
                "INFO",
            )
        except Exception as e:
            self.append_log(f"Failed to update {CONFIG_PATH}: {e}", "ERROR")

    # ---------------------------
    # Login (DB-backed)
    # ---------------------------

    def on_proceed_login(self):
        email = self.login_email.text().strip().lower()
        pin = self.login_password.text().strip()
        vci_mode = self.login_vci.currentData()  # "pcan" or "socketcan"

        if not email or not pin:
            QMessageBox.warning(self, "Login Error", "Email and PIN are required.")
            return

        try:
            user = db_layer.get_user_by_email(email)
            if not user:
                QMessageBox.warning(self, "Login Error", "No such user found. Please register first.")
                return

            pin_hash = user.get("pin_hash")
            if isinstance(pin_hash, str):
                pin_hash = pin_hash.encode("utf-8")

            if not db_layer.check_pin(pin, pin_hash):
                QMessageBox.warning(self, "Login Error", "Invalid email or PIN.")
                return

            self.user_email = email
            self.user_name = user.get("name", "")
            self.user_empid = user.get("emp_id", "")

            self._apply_vci_selection(vci_mode)
            self.append_log(
                f"Logged in as {self.user_name} (VCI: {self.login_vci.currentText()})",
                "INFO",
            )
            self.stack.setCurrentWidget(self.dashboard)  # To dashboard
        except Exception as e:
            QMessageBox.warning(self, "Login Error", f"Login failed: {e}")
            self.append_log(f"Login Exception: {e}", "ERROR")

    # Helper: find model tests directory (supports spaces/underscores)
    def find_model_tests_dir(self, model_name: str) -> Optional[str]:
        base_root = TEST_FOLDER  # already absolute
        candidates = [
            model_name,
            model_name.replace(' ', '_'),
            model_name.replace('_', ' ')
        ]
        seen = set()
        uniq = []
        for c in candidates:
            if c not in seen:
                uniq.append(c)
                seen.add(c)

        for sub in uniq:
            p = os.path.join(base_root, sub)
            if os.path.isdir(p):
                return p
        return None

    def build_styled_button(self, text: str, style_key: str, callback: callable) -> QPushButton:
        btn = QPushButton(text)
        btn.setStyleSheet(STYLES[style_key])
        btn.setToolTip("")
        if callback:
            btn.clicked.connect(callback)
        return btn

    # ---------------------------
    # Dashboard Page
    # ---------------------------

    def build_dashboard_page(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)

        # VIN Entry
        vin_layout = QHBoxLayout()
        vin_label = QLabel("ENTER VIN :")
        vin_label.setFont(QFont("Arial", 8, QFont.Bold))
        vin_label.setToolTip("")

        self.vin_input = QLineEdit()
        self.vin_input.setPlaceholderText("e.g., MDXXXXXXXXXXXXXXX")
        self.vin_input.setStyleSheet(STYLES["INPUT"])
        self.vin_input.setToolTip("")
        self.vin_input.setMaxLength(17)
        vin_regex = QRegExp("[A-Za-z0-9]{0,17}")
        self.vin_input.setValidator(QRegExpValidator(vin_regex, self.vin_input))
        self.vin_input.textChanged.connect(self._enforce_vin_upper)
        self.vin_input.textChanged.connect(self.on_vin_changed)

        vin_layout.addWidget(vin_label)
        vin_layout.addWidget(self.vin_input, 1)

        clear_vin_btn = self.build_styled_button("CLEAR", "BUTTON_SECONDARY", self.clear_selection)
        vin_layout.addWidget(clear_vin_btn)

        layout.addLayout(vin_layout)

        # Vehicle Type Selection
        type_label = QLabel("VEHICLE TYPE")
        type_label.setFont(QFont("Arial", 10, QFont.Bold))
        type_label.setToolTip("")
        layout.addWidget(type_label)

        type_layout = QHBoxLayout()
        types = [
            ("ALL MODELS", os.path.join(ASSETS_FOLDER, "All_Models.png")),
            ("MOTOR CYCLE", os.path.join(ASSETS_FOLDER, "motor_cycle.png")),
            ("SCOOTER", os.path.join(ASSETS_FOLDER, "scooter.png")),
            ("3-WHEELER", os.path.join(ASSETS_FOLDER, "3_Wheeler.png")),
        ]
        self.category_buttons: dict = {}

        for type_name, img_path in types:
            cat_frame = QFrame()
            cat_frame.setFixedHeight(140)
            cat_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            cat_frame.setStyleSheet(STYLES["CATEGORY_FRAME"])
            cat_frame.setToolTip("")
            cat_frame.setAttribute(Qt.WA_AcceptTouchEvents, True)
            cat_frame.grabGesture(Qt.TapGesture)
            cat_frame.grabGesture(Qt.PanGesture)

            cat_layout = QVBoxLayout(cat_frame)
            cat_layout.setSpacing(1)
            cat_layout.setContentsMargins(10, 10, 10, 10)

            img_label = QLabel()
            img_label.setAlignment(Qt.AlignCenter)
            img_label.setToolTip("")
            img_label.setStyleSheet("border: 1px solid #ddd; border-radius: 5px; background-color: lightgray;")

            if img_path and os.path.exists(img_path):
                pix = QPixmap(img_path).scaled(60, 60, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                img_label.setPixmap(pix)
            else:
                img_label.setText("[Icon]")
                img_label.setStyleSheet("font-size: 20px; color: gray; border: none; background-color: transparent;")

            cat_layout.addWidget(img_label)

            text_label = QLabel(type_name)
            text_label.setAlignment(Qt.AlignCenter)
            text_label.setFont(QFont("Arial", 8, QFont.Bold))
            text_label.setToolTip("")
            text_label.setStyleSheet("border: none; background-color: transparent;")
            cat_layout.addWidget(text_label)

            cat_frame.type_name = type_name
            cat_frame.mousePressEvent = lambda event, t=type_name, f=cat_frame: self._on_category_clicked(t, f)

            type_layout.addWidget(cat_frame)
            self.category_buttons[type_name] = cat_frame

        type_layout.addStretch()
        layout.addLayout(type_layout)

        # Search Model
        search_layout = QHBoxLayout()
        search_label = QLabel("SEARCH MODEL : ")
        search_label.setFont(QFont("Arial", 8, QFont.Bold))
        search_label.setToolTip("")

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("e.g., TVS XL")
        self.search_input.setStyleSheet(STYLES["INPUT"])
        self.search_input.setToolTip("")
        self.search_input.textChanged.connect(self.on_search_changed)

        reset_btn = self.build_styled_button("RESET", "BUTTON_SECONDARY", self.reset_dashboard)
        reset_btn.setFixedHeight(38)

        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_input, 1)
        search_layout.addWidget(reset_btn)
        layout.addLayout(search_layout)

        # Models List
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFixedHeight(450)
        self.scroll.setToolTip("")

        self.models_widget = QWidget()
        self.models_layout = QVBoxLayout(self.models_widget)
        self.models_layout.setSpacing(10)

        self.model_frames: dict = {}
        self.update_models_display()
        self.scroll.setWidget(self.models_widget)
        layout.addWidget(self.scroll)

        # Quick Log Preview
        layout.addSpacing(20)
        log_label = QLabel("<b>LOG PREVIEW</b>")
        log_label.setToolTip("")
        layout.addWidget(log_label)

        self.quick_log = QTextEdit()
        self.quick_log.setReadOnly(True)
        self.quick_log.setFixedHeight(150)
        self.quick_log.setObjectName("quick_log")
        self.quick_log.setStyleSheet(STYLES["LOG_TEXT"])
        self.quick_log.setToolTip("")
        layout.addWidget(self.quick_log)

        log_buttons_layout = QHBoxLayout()
        save_btn = self.build_styled_button("SAVE LOG", "BUTTON_SECONDARY", self.SAVE_LOG)
        clear_btn = self.build_styled_button("CLEAR LOGS", "BUTTON_SECONDARY", self.CLEAR_LOGS)
        back_to_login_btn = self.build_styled_button(
            "BACK", "BUTTON_SECONDARY", lambda: self.stack.setCurrentWidget(self.login_page)
        )
        log_buttons_layout.addStretch()
        log_buttons_layout.addWidget(save_btn)
        log_buttons_layout.addWidget(clear_btn)
        log_buttons_layout.addWidget(back_to_login_btn)
        layout.addLayout(log_buttons_layout)

        # Default category: ALL MODELS
        if "ALL MODELS" in self.category_buttons:
            self._on_category_clicked("ALL MODELS", self.category_buttons["ALL MODELS"])

        return w

    def _on_category_clicked(self, vehicle_type: str, frame: QFrame) -> None:
        if self.current_category_frame and self.current_category_frame != frame:
            self.current_category_frame.setStyleSheet(STYLES["CATEGORY_FRAME"])

        frame.setStyleSheet(STYLES["CATEGORY_SELECTED"])
        self.current_category_frame = frame
        self.current_filter = vehicle_type
        self.update_models_display()
        self.append_log(f"Vehicle type selected: {vehicle_type}", "INFO")

    def event(self, event):
        if event.type() == QEvent.Gesture:
            gesture = event.gesture(Qt.TapGesture)
            if gesture and gesture.state() == Qt.GestureFinished:
                self.append_log("Tap gesture detected on category", "DEBUG")
                return True
            pan_gesture = event.gesture(Qt.PanGesture)
            if pan_gesture and (pan_gesture.state() == Qt.GestureStarted or pan_gesture.state() == Qt.GestureUpdated):
                delta = pan_gesture.delta()
                if abs(delta.x()) > 50:
                    direction = "right" if delta.x() > 0 else "left"
                    self.cycle_categories(direction)
                    return True
        return super().event(event)

    def cycle_categories(self, direction: str):
        categories = list(self.category_buttons.keys())
        current_idx = categories.index(self.current_filter) if self.current_filter in categories else 0
        if direction == "left":
            next_idx = (current_idx + 1) % len(categories)
        else:
            next_idx = (current_idx - 1) % len(categories)
        next_cat = categories[next_idx]
        self._on_category_clicked(next_cat, self.category_buttons[next_cat])
        self.append_log(f"Swiped to {next_cat}", "INFO")

    def reset_dashboard(self) -> None:
        self.suppress_vin_change = True
        with QSignalBlocker(self.vin_input):
            self.vin_input.clear()
        with QSignalBlocker(self.search_input):
            self.search_input.clear()

        self.vin_filter_text = ""
        self.search_text = ""
        self.selected_vehicle = None
        self.active_model = None
        self.active_model_dir = None
        self.clear_highlights()

        default_cat = "ALL MODELS" if "ALL MODELS" in self.category_buttons else next(
            iter(self.category_buttons.keys()), None
        )
        if default_cat:
            self._on_category_clicked(default_cat, self.category_buttons[default_cat])
        else:
            self.update_models_display()

        if self.scroll and self.scroll.verticalScrollBar():
            self.scroll.verticalScrollBar().setValue(0)

        self.append_log("Dashboard reset.", "INFO")
        QTimer.singleShot(0, lambda: setattr(self, 'suppress_vin_change', False))

    def clear_selection(self) -> None:
        self.suppress_vin_change = True
        with QSignalBlocker(self.vin_input):
            self.vin_input.clear()
        self.vin_filter_text = ""

        if self.selected_vehicle:
            self.selected_vehicle = None
            self.active_model = None
            self.active_model_dir = None
            self.clear_highlights()
            self.append_log("Selection cleared.", "INFO")
        else:
            self.append_log("VIN cleared.", "INFO")

        self.update_models_display()
        QTimer.singleShot(0, lambda: setattr(self, 'suppress_vin_change', False))

    def _enforce_vin_upper(self, text: str) -> None:
        up = text.upper()
        if self.vin_input.text() != up:
            pos = self.vin_input.cursorPosition()
            with QSignalBlocker(self.vin_input):
                self.vin_input.setText(up)
            self.vin_input.setCursorPosition(pos)

    def on_search_changed(self, text: str) -> None:
        self.search_text = text.lower()
        self.update_models_display()

    def on_vin_changed(self, text: str) -> None:
        if self.suppress_vin_change:
            return

        s = text.strip().upper()
        if len(s) < 7:
            self.vin_filter_text = ""
            self.clear_highlights()
            self.selected_vehicle = None
            self.update_models_display()
            return

        matches = [
            (name, details, vin_ph, category)
            for (name, details, vin_ph, category) in VEHICLE_MODELS
            if vin_matches(vin_ph, s)
        ]

        if not matches:
            self.vin_filter_text = ""
            self.clear_highlights()
            self.selected_vehicle = None
            self.update_models_display()
            return

        self.vin_filter_text = s
        self.update_models_display()

        if self.search_text:
            with QSignalBlocker(self.search_input):
                self.search_input.clear()
            self.search_text = ""

        if len(matches) == 1:
            name, _, vin_placeholder, _ = matches[0]
            self.selected_vehicle = name
            self.highlight_vehicle(name)
            if self.vin_input.text().upper() != vin_placeholder.upper():
                with QSignalBlocker(self.vin_input):
                    self.vin_input.setText(vin_placeholder)
        else:
            self.clear_highlights()
            self.selected_vehicle = None

    def on_vehicle_selected(self, vehicle_name: str, vin_placeholder: str) -> None:
        self.selected_vehicle = vehicle_name
        self.vin_input.setText(vin_placeholder)
        self.highlight_vehicle(vehicle_name)

        model_dir = None
        if vehicle_name == "TVS iQube ST":
            model_dir = self.find_model_tests_dir("TVS iQube ST")
            if model_dir and os.path.exists(os.path.join(model_dir, "tests.json")):
                self.append_log(f'Loading sub-programs for "{vehicle_name}" from {model_dir}', "INFO")
            else:
                self.append_log(f'Folder or tests.json missing for "{vehicle_name}"', "WARNING", color="red")
                model_dir = None
        else:
            self.append_log(
                f'Currently, we haven\'t deployed sub-programs for "{vehicle_name}" yet (future support via elif)',
                "WARNING",
                color="red",
            )
            model_dir = None

        if not model_dir:
            self.active_model = vehicle_name
            self.active_model_dir = None
            self.rebuild_tests_for_active_model()
            return

        manifest = self._load_model_manifest(model_dir)
        if not manifest:
            self.active_model = vehicle_name
            self.active_model_dir = None
            self.append_log(f'tests.json invalid/empty for "{vehicle_name}"', "WARNING", color="red")
            self.rebuild_tests_for_active_model()
            return

        self.active_model = vehicle_name
        self.active_model_dir = model_dir
        self._current_manifest_tests = manifest

        self.rebuild_tests_for_active_model()
        self.append_log(f'"{vehicle_name}" ready: {len(manifest)} sub-programs loaded', "INFO", color="green")

        QTimer.singleShot(200, lambda: self.stack.setCurrentWidget(self.tests_page))

    def update_models_display(self) -> None:
        if self.vin_filter_text:
            self.filtered_models_cache = [
                m for m in VEHICLE_MODELS if vin_matches(m[2], self.vin_filter_text)
            ]
        else:
            self.filtered_models_cache = [
                m for m in VEHICLE_MODELS
                if (self.current_filter == "ALL MODELS" or m[3] == self.current_filter)
                and (not self.search_text or self.search_text in m[0].lower())
            ]

        # Clear layout
        for i in reversed(range(self.models_layout.count())):
            child = self.models_layout.itemAt(i).widget()
            if child:
                child.deleteLater()
        self.model_frames.clear()

        for (name, details, vin_placeholder, _) in self.filtered_models_cache:
            model_frame = self.ClickableFrame()
            model_frame.setFrameStyle(QFrame.NoFrame)
            model_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            model_frame.setFixedHeight(140)
            model_frame.setStyleSheet(STYLES["MODEL_FRAME"])
            model_frame.setToolTip("")

            model_layout = QHBoxLayout(model_frame)
            model_layout.setContentsMargins(10, 5, 10, 5)

            img_label = QLabel()
            img_label.setFixedSize(100, 100)
            img_label.setStyleSheet("border: 1px solid #ddd; border-radius: 5px; background-color: lightgray;")
            img_label.setToolTip("")

            img_path = VEHICLE_IMAGES.get(name, "")
            pix = QPixmap(img_path) if img_path and os.path.exists(img_path) else QPixmap()
            if not pix.isNull():
                pix = pix.scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                img_label.setPixmap(pix)
            else:
                img_label.setText("[Image]")
                img_label.setAlignment(Qt.AlignCenter)

            model_layout.addWidget(img_label)

            text_layout = QVBoxLayout()
            text_layout.setSpacing(2)
            text_layout.setContentsMargins(0, 0, 0, 0)

            name_label = QLabel(name)
            name_label.setFont(QFont("Arial", 11, QFont.Bold))
            name_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            name_label.setStyleSheet("border: none; background-color: transparent;")

            vin_label = QLabel(vin_placeholder)
            vin_label.setFont(QFont("Arial", 9))
            vin_label.setStyleSheet("color: gray; border: none; background-color: transparent;")

            details_label = QLabel(details)
            details_label.setFont(QFont("Arial", 10))
            details_label.setStyleSheet("border: none; background-color: transparent;")

            text_layout.addWidget(name_label)
            text_layout.addWidget(vin_label)
            text_layout.addWidget(details_label)

            model_layout.addLayout(text_layout)
            model_layout.addStretch()

            model_frame.vehicle_name = name
            model_frame.vehicle_vin = vin_placeholder

            if ON_CLICK == 'single':
                model_frame.mousePressEvent = lambda e, f=model_frame: self.on_vehicle_selected(
                    f.vehicle_name, f.vehicle_vin
                )
                model_frame.mouseDoubleClickEvent = lambda e, f=model_frame: self.clear_selection()
            else:  # double-click
                model_frame.mousePressEvent = lambda e, f=model_frame: None
                model_frame.mouseDoubleClickEvent = lambda e, f=model_frame: self.on_vehicle_selected(
                    f.vehicle_name, f.vehicle_vin
                )

            self.models_layout.addWidget(model_frame)
            self.model_frames[name] = model_frame

        if not self.filtered_models_cache:
            no_results_label = QLabel("No matching models found.")
            no_results_label.setAlignment(Qt.AlignCenter)
            no_results_label.setStyleSheet(
                "color: gray; font-style: italic; border: none; background-color: transparent;"
            )
            self.models_layout.addWidget(no_results_label)

    def highlight_vehicle(self, vehicle_name: str, highlight_color: str = "lightblue") -> None:
        self.clear_highlights()
        if vehicle_name in self.model_frames:
            self.model_frames[vehicle_name].setStyleSheet(STYLES["MODEL_HIGHLIGHT"])

    def clear_highlights(self) -> None:
        for frame in self.model_frames.values():
            frame.setStyleSheet(STYLES["MODEL_FRAME"])

    class ClickableFrame(QFrame):
        def __init__(self, parent=None):
            super().__init__(parent)
            self.vehicle_name = ""
            self.vehicle_vin = ""

    # ----- Logs navigation helpers -----
    def show_logs_from(self, origin_widget):
        self._logs_return_to = origin_widget
        self.stack.setCurrentWidget(self.log_page)

    def _go_back_from_logs(self):
        target = self._logs_return_to or self.dashboard
        self.stack.setCurrentWidget(target)

    # ---------------------------
    # Tests Page
    # ---------------------------

    def build_tests_page(self) -> QWidget:
        w = QWidget()
        outer = QVBoxLayout(w)
        outer.setContentsMargins(20, 20, 20, 20)
        outer.setSpacing(10)

        hdr = QHBoxLayout()
        title = QLabel("<h2>TEST SEQUENCES</h2>")
        title.setStyleSheet("border: none; background: transparent;")
        hdr.addWidget(title)
        hdr.addStretch()

        back_btn = self.build_styled_button(
            "BACK", "BUTTON_SECONDARY", lambda: self.stack.setCurrentWidget(self.dashboard)
        )
        hdr.addWidget(back_btn)
        outer.addLayout(hdr)

        controls = QHBoxLayout()
        run_all_btn = self.build_styled_button("RUN ALL", "BUTTON_PRIMARY", self.run_all_tests)
        self.run_all_progress = QProgressBar()
        self.run_all_progress.setVisible(False)
        self.run_all_progress.setFixedHeight(22)
        self.run_all_progress.setTextVisible(False)

        self.stop_btn = self.build_styled_button("STOP", "BUTTON_SECONDARY", self.stop_run_all)
        self.stop_btn.hide()
        self.hide_btn = self.build_styled_button("HIDE", "BUTTON_SECONDARY", self.hide_run_all_controls)
        self.hide_btn.hide()

        view_log_btn = self.build_styled_button("VIEW LOG", "BUTTON_SECONDARY", lambda: self.show_logs_from(w))

        controls.addWidget(run_all_btn)
        controls.addWidget(self.run_all_progress, 1)
        controls.addWidget(self.stop_btn)
        controls.addWidget(self.hide_btn)
        controls.addStretch()
        controls.addWidget(view_log_btn)
        outer.addLayout(controls)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet("""
            QScrollArea { border: none; }
            QScrollBar:vertical {
                background: transparent;
                width: 14px;
                margin: 6px 2px 6px 2px;
                border-radius: 7px;
            }
            QScrollBar::handle:vertical {
                background: #9aa9b2;
                min-height: 40px;
                border-radius: 7px;
            }
            QScrollBar::handle:vertical:hover {
                background: #7c8a93;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px; background: transparent; border: none;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: transparent;
            }
        """)

        container = QWidget()
        v = QVBoxLayout(container)
        v.setSpacing(12)
        v.setContentsMargins(0, 0, 0, 0)
        self.tests_container_layout = v
        self.tests_scroll = scroll

        v.addWidget(QLabel("Select a vehicle with deployed tests to view available test sequence."))
        v.addStretch()

        scroll.setWidget(container)
        outer.addWidget(scroll)
        return w

    def _load_model_manifest(self, model_dir: str) -> Optional[List[dict]]:
        manifest_path = os.path.join(model_dir, "tests.json")
        if not os.path.isfile(manifest_path):
            return None
        try:
            with open(manifest_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            tests = data.get("tests", [])
            valid = []
            for item in tests:
                if all(k in item for k in ("label", "module", "function")):
                    valid.append(item)
            return valid or None
        except Exception as e:
            self.append_log(f"Manifest parse error in {manifest_path}: {e}", "WARNING")
            return None

    def rebuild_tests_for_active_model(self) -> None:
        if not self.tests_container_layout:
            return

        layout = self.tests_container_layout
        while layout.count():
            item = layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

        self.test_rows.clear()

        if not self.active_model or not self.active_model_dir:
            layout.addWidget(QLabel("No tests deployed for the selected vehicle model."))
            layout.addStretch()
            return

        tests = self._load_model_manifest(self.active_model_dir)
        if not tests:
            layout.addWidget(
                QLabel(f'No tests.json found or no tests in "{os.path.basename(self.active_model_dir)}".')
            )
            layout.addStretch()
            return

        for item in tests:
            label = item["label"]
            module_name = item["module"]
            func_name = item["function"]
            requires_mac = bool(item.get("requires_mac")) or label.lower().startswith("write tpms")
            proceed_text = item.get("button") or item.get("button_text") or "Proceed"

            card = self._create_test_card(
                label, module_name, func_name, requires_mac=requires_mac, proceed_text=proceed_text
            )
            layout.addWidget(card)

        layout.addStretch()

        if self.tests_scroll:
            self.tests_scroll.verticalScrollBar().setValue(0)

    def _create_test_card(self, label: str, module_name: str, func_name: str,
                          requires_mac: bool = False, proceed_text: str = "Proceed") -> QWidget:
        card = QFrame()
        card.setStyleSheet(STYLES["TEST_CARD"])
        card.setFrameStyle(QFrame.NoFrame)
        card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        card.setMinimumHeight(110)

        inner = QVBoxLayout(card)
        inner.setContentsMargins(14, 12, 14, 12)
        inner.setSpacing(8)

        top = QHBoxLayout()
        name_lbl = QLabel(f"{label}")
        name_lbl.setFont(QFont("Arial", 12, QFont.Bold))
        name_lbl.setStyleSheet("border: none; background-color: transparent;")
        top.addWidget(name_lbl)
        top.addStretch()
        inner.addLayout(top)

        mac_input = None
        mid = QHBoxLayout()
        if requires_mac:
            mac_input = QLineEdit()
            mac_input.setPlaceholderText("AABBCCDDEEFF")
            mac_input.setStyleSheet(STYLES["INPUT"])
            mac_input.setMinimumWidth(320)
            mac_input.setMaxLength(12)
            mac_regex = QRegExp("[0-9A-Fa-f]{0,12}")
            mac_input.setValidator(QRegExpValidator(mac_regex, mac_input))
            mac_input.textChanged.connect(lambda text, inp=mac_input: self._validate_mac(text, inp))
            mid.addWidget(mac_input)
        else:
            mid.addStretch()
        inner.addLayout(mid)

        bot = QHBoxLayout()
        proceed_btn = self.build_styled_button(proceed_text, "BUTTON_PRIMARY", partial(self.on_proceed_clicked, label))
        actual_lbl = QLabel("")
        actual_lbl.setStyleSheet("color: blue; border: none; background: transparent;")
        actual_lbl.setMinimumWidth(150)
        result_lbl = QLabel("Idle")
        result_lbl.setStyleSheet(STYLES["TEST_RESULT_IDLE"])
        result_lbl.setMinimumWidth(100)

        bot.addWidget(proceed_btn)
        bot.addStretch()
        bot.addWidget(actual_lbl)
        bot.addWidget(result_lbl)

        inner.addLayout(bot)

        self.test_rows[label] = TestRow(module_name, func_name, mac_input, proceed_btn, result_lbl, actual_lbl)
        return card

    def _validate_mac(self, text: str, input_widget: QLineEdit) -> None:
        try:
            parse_mac_input(text)
            input_widget.setStyleSheet(STYLES["INPUT"])
        except ValueError:
            input_widget.setStyleSheet(
                "font-size: 14px; padding: 10px; border: 2px solid red; "
                "border-radius: 10px; background-color: white;"
            )

    def is_valid_for_run(self, label: str) -> bool:
        row = self.test_rows.get(label)
        if not row:
            return False
        return not row.mac_input or bool(row.mac_input.text().strip())

    # ---------------------------
    # Log Page
    # ---------------------------

    def build_log_page(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(20, 20, 20, 20)

        hdr = QHBoxLayout()
        title = QLabel("<h2>LOGS</h2>")
        title.setStyleSheet("border: none; background: transparent;")
        hdr.addWidget(title)
        hdr.addStretch()
        hdr.addWidget(self.build_styled_button("BACK", "BUTTON_SECONDARY", self._go_back_from_logs))
        layout.addLayout(hdr)

        self.full_log = QTextEdit()
        self.full_log.setReadOnly(True)
        self.full_log.setStyleSheet(STYLES["LOG_TEXT"])
        layout.addWidget(self.full_log)

        save_btn = self.build_styled_button("SAVE LOG", "BUTTON_SECONDARY", self.SAVE_LOG)
        layout.addWidget(save_btn)
        return w

    def append_log(self, text: str, level: str = "INFO", color: Optional[str] = None) -> None:
        # Log to Python logging system (for external modules, file handler could be added in future)
        logger.log(getattr(logging, level), text, extra={"skip_gui": True})

        # Log to GUI only
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        line = f"[{ts}] {text}"

        if self.full_log:
            self.full_log.append(f'<span style="color:{color}">{line}</span>' if color else line)
            self.full_log.verticalScrollBar().setValue(self.full_log.verticalScrollBar().maximum())

        if self.quick_log:
            self.quick_log.append(f'<span style="color:{color}">{line}</span>' if color else line)
            self.quick_log.verticalScrollBar().setValue(self.quick_log.verticalScrollBar().maximum())

    def SAVE_LOG(self) -> None:
        # Logs are saved ONLY when this button is pressed
        filename = f"{LOG_BASENAME}_ui.txt"
        path = os.path.join(LOG_FOLDER, filename)
        try:
            with open(path, "w", encoding="utf-8") as f:
                text_plain = self.full_log.toPlainText() if self.full_log else ""
                f.write(text_plain)
            self.append_log(f"Log saved to: {path}", "INFO")
            QMessageBox.information(self, "Saved", f"Log saved to {path}")
        except Exception as e:
            self.append_log(f"Error saving log: {e}", "ERROR")
            QMessageBox.warning(self, "Save Error", f"Failed to SAVE LOG: {e}")

    def CLEAR_LOGS(self) -> None:
        if self.full_log:
            self.full_log.clear()
        if self.quick_log:
            self.quick_log.clear()
        self.append_log("Logs cleared.", "INFO")

    # ---------------------------
    # Test classification and execution
    # ---------------------------

    def _classify_tpms_test(self, label: str, module_name: str, func_name: str) -> str:
        l = label.lower()
        if 'tpms' in l:
            front = 'front' in l
            rear = 'rear' in l
            write = 'write' in l
            read = 'read' in l
            if write and front:
                return 'write_front'
            if write and rear:
                return 'write_rear'
            if read and front:
                return 'read_front'
            if read and rear:
                return 'read_rear'

        f = func_name.lower()
        m = module_name.lower()
        if 'tpms' in f or 'tpms' in m:
            if 'write' in f and 'front' in f:
                return 'write_front'
            if 'write' in f and 'rear' in f:
                return 'write_rear'
            if 'read' in f and 'front' in f:
                return 'read_front'
            if 'read' in f and 'rear' in f:
                return 'read_rear'

        return 'generic'

    def on_proceed_clicked(self, label: str) -> None:
        if not self.active_model_dir:
            self.append_log("No test sequence deployed for the selected vehicle.", "WARNING", color="red")
            return

        if not check_can_connection():
            row = self.test_rows[label]
            row.result.setText("Error")
            row.result.setStyleSheet(STYLES["TEST_RESULT_FAIL"])
            self.append_log(f"VCI not connected for {label}", "WARNING")
            row.btn.setEnabled(True)

            if QMessageBox.question(self, "VCI Error", "VCI not connected. Retry?") == QMessageBox.Yes:
                if check_can_connection():
                    self.on_proceed_clicked(label)
            return

        self._run_single_test(label)

    def _get_test_fn(self, module_name: str, func_name: str):
        if not self.active_model_dir:
            raise RuntimeError("Active model test folder is not set.")
        key = (self.active_model_dir, module_name, func_name)
        if key not in self.test_fn_cache:
            self.test_fn_cache[key] = import_callable_from_dir(self.active_model_dir, module_name, func_name)
        return self.test_fn_cache[key]

    def _run_single_test(self, label: str) -> None:
        row = self.test_rows[label]
        btn = row.btn
        res_lbl = row.result

        btn.setEnabled(False)
        res_lbl.setText("Running...")
        res_lbl.setStyleSheet(STYLES["TEST_RESULT_RUNNING"])
        if row.actual:
            row.actual.setText("")

        self.append_log(f"Starting: {label}", "INFO")

        module_name, func_name = row.module, row.func
        try:
            fn = self._get_test_fn(module_name, func_name)
        except Exception as e:
            self.append_log(f"Import error for {label}: {e}", "ERROR")
            res_lbl.setText("Import Error")
            res_lbl.setStyleSheet(STYLES["TEST_RESULT_FAIL"])
            btn.setEnabled(True)
            return

        args = []
        kind = self._classify_tpms_test(label, module_name, func_name)

        if kind in ('write_front', 'write_rear'):
            if row.mac_input is None:
                self.append_log(f"{label}: MAC input missing.", "WARNING")
                res_lbl.setText("Invalid MAC")
                res_lbl.setStyleSheet(STYLES["TEST_RESULT_FAIL"])
                btn.setEnabled(True)
                return

            raw = row.mac_input.text().strip()
            try:
                parse_mac_input(raw)
            except ValueError as e:
                res_lbl.setText("Invalid MAC")
                res_lbl.setStyleSheet(STYLES["TEST_RESULT_FAIL"])
                btn.setEnabled(True)
                QMessageBox.warning(self, "Invalid MAC", str(e))
                self.append_log(f"Invalid MAC for {label}: {e}", "WARNING")
                return

            mac_hex = raw.upper()
            args = [mac_hex]

        elif kind == 'read_front':
            expected = self.tpms_macs.get('front')
            if not expected:
                res_lbl.setText("No Front MAC")
                res_lbl.setStyleSheet(STYLES["TEST_RESULT_FAIL"])
                btn.setEnabled(True)
                QMessageBox.warning(self, "Missing MAC", "Front MAC not written yet. Run 'Write TPMS Front' first.")
                self.append_log("Read TPMS Front blocked: no stored Front MAC.", "WARNING")
                return
            args = [expected]
            self.append_log(f"Passing expected Front MAC '{expected}' to {label}", "DEBUG")

        elif kind == 'read_rear':
            expected = self.tpms_macs.get('rear')
            if not expected:
                res_lbl.setText("No Rear MAC")
                res_lbl.setStyleSheet(STYLES["TEST_RESULT_FAIL"])
                btn.setEnabled(True)
                QMessageBox.warning(self, "Missing MAC", "Rear MAC not written yet. Run 'Write TPMS Rear' first.")
                self.append_log("Read TPMS Rear blocked: no stored Rear MAC.", "WARNING")
                return
            args = [expected]
            self.append_log(f"Passing expected Rear MAC '{expected}' to {label}", "DEBUG")

        else:
            if row.mac_input:
                try:
                    mac_bytes = parse_mac_input(row.mac_input.text())
                except ValueError as e:
                    res_lbl.setText("Invalid MAC")
                    res_lbl.setStyleSheet(STYLES["TEST_RESULT_FAIL"])
                    btn.setEnabled(True)
                    QMessageBox.warning(self, "Invalid MAC", str(e))
                    self.append_log(f"Invalid MAC for {label}: {e}", "WARNING")
                    return
                args = [mac_bytes]

        def run_with_capture():
            # Capture prints from the test into GUI as well
            out = EmittingStream(self._log_emitter, level="INFO")
            err = EmittingStream(self._log_emitter, level="ERROR")
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                result = fn(*args) if args else fn()
                out.flush()
                err.flush()
                return result

        worker = Worker(run_with_capture)
        worker.signals.finished.connect(partial(self.on_test_finished, label))
        worker.signals.error.connect(partial(self.on_test_error, label))
        self.threadpool.start(worker)

    def on_test_finished(self, label: str, result: Any) -> None:
        row = self.test_rows[label]
        kind = self._classify_tpms_test(label, row.module, row.func)

        if isinstance(result, tuple) and len(result) == 2:
            passed, actual = result
            row.result.setText("PASS" if passed else "FAIL")
            row.result.setStyleSheet(STYLES["TEST_RESULT_PASS"] if passed else STYLES["TEST_RESULT_FAIL"])
            if row.actual is not None:
                row.actual.setText(str(actual) if actual else "")
                row.actual.setStyleSheet("color: blue; background: transparent; border: none;")
            self.append_log(f"{label} -> {'PASS' if passed else 'FAIL'} (Value: {actual})", "INFO")

            if passed and kind in ('write_front', 'write_rear') and row.mac_input:
                mac_key = 'front' if kind == 'write_front' else 'rear'
                stored_mac = row.mac_input.text().strip().upper()
                self.tpms_macs[mac_key] = stored_mac
                if row.actual is not None:
                    row.actual.setText(stored_mac)
                self.append_log(f"Stored {mac_key.capitalize()} MAC: {stored_mac}", "INFO")

        else:
            if isinstance(result, str) and kind in ('read_front', 'read_rear'):
                actual = result.strip().upper()
                expected = self.tpms_macs.get('front' if kind == 'read_front' else 'rear')
                passed = bool(expected and actual == expected.upper())
                row.result.setText("PASS" if passed else "FAIL")
                row.result.setStyleSheet(STYLES["TEST_RESULT_PASS"] if passed else STYLES["TEST_RESULT_FAIL"])
                if row.actual is not None:
                    row.actual.setText(actual)
                self.append_log(
                    f"{label} -> {'PASS' if passed else 'FAIL'} (Value: {actual}, Expected: {expected})",
                    "INFO",
                )
            else:
                if isinstance(result, bool):
                    status, color_style = (
                        ("PASS", STYLES["TEST_RESULT_PASS"])
                        if result
                        else ("FAIL", STYLES["TEST_RESULT_FAIL"])
                    )
                    row.result.setText(status)
                    row.result.setStyleSheet(color_style)
                    self.append_log(f"{label} -> {status}", "INFO")
                elif isinstance(result, (int, float, str)):
                    row.result.setText(str(result))
                    row.result.setStyleSheet(STYLES["TEST_RESULT_PASS"])
                    if row.actual is not None and kind.startswith("read_"):
                        row.actual.setText(str(result))
                    self.append_log(f"{label} -> {result}", "INFO")
                elif isinstance(result, (bytes, bytearray)):
                    hexs = " ".join(f"{b:02X}" for b in result)
                    row.result.setText(hexs)
                    row.result.setStyleSheet(STYLES["TEST_RESULT_PASS"])
                    if row.actual is not None:
                        row.actual.setText(hexs)
                    self.append_log(f"{label} -> {hexs}", "INFO")
                else:
                    row.result.setText(str(result))
                    row.result.setStyleSheet(STYLES["TEST_RESULT_PASS"])
                    self.append_log(f"{label} -> {result}", "INFO")

        row.btn.setEnabled(True)

        if self.run_all_mode:
            self.completed_tests += 1
            self.run_all_progress.setValue(self.completed_tests)

            if self.run_all_mode == 'strict':
                if self.run_all_stopped:
                    self._finish_run_all()
                    return

                failed = (isinstance(result, tuple) and (not result[0])) or (isinstance(result, bool) and (not result))
                if failed:
                    self.append_log(f"Run All stopped: {label} failed.", "WARNING")
                    self._finish_run_all()
                    return

                if self.test_queue:
                    self._run_next_queued_test()
                else:
                    self._finish_run_all()

    def on_test_error(self, label: str, errtb: Tuple[Exception, str]) -> None:
        err, tb = errtb
        row = self.test_rows[label]
        row.result.setText("ERROR")
        row.result.setStyleSheet(STYLES["TEST_RESULT_FAIL"])
        row.btn.setEnabled(True)
        self.append_log(f"Error during {label}: {err}", "ERROR")
        self.append_log(tb, "DEBUG")

        if self.run_all_mode:
            self.completed_tests += 1
            self.run_all_progress.setValue(self.completed_tests)
            if self.run_all_mode == 'strict':
                self.append_log(f"Run All stopped: error in {label}", "ERROR")
                self._finish_run_all()
                return

    def run_all_tests(self) -> None:
        if not self.active_model_dir:
            self.append_log("No test sequence deployed for the selected vehicle.", "WARNING", color="red")
            return

        if not check_can_connection():
            self.append_log("VCI not connected. Cannot run all tests.", "WARNING")
            QMessageBox.warning(
                self,
                "VCI Error",
                "VCI not connected.\n\nConnect the interface and try RUN ALL again."
            )
            return

        valid_labels = []
        for label, row in self.test_rows.items():
            kind = self._classify_tpms_test(label, row.module, row.func)
            if kind == 'read_front' and not self.tpms_macs.get('front'):
                self.append_log(f"Skipping {label}: Front MAC not written yet.", "WARNING")
                continue
            if kind == 'read_rear' and not self.tpms_macs.get('rear'):
                self.append_log(f"Skipping {label}: Rear MAC not written yet.", "WARNING")
                continue

            if (row.mac_input is None) or bool(row.mac_input.text().strip()):
                valid_labels.append(label)

        if not valid_labels:
            self.append_log("No valid tests to run (check MAC inputs).", "WARNING")
            return

        self.test_queue = valid_labels[:]
        self.pending_tests = len(valid_labels)
        self.completed_tests = 0
        self.run_all_progress.setMaximum(self.pending_tests)
        self.run_all_progress.setValue(0)
        self.run_all_progress.setVisible(True)
        self.run_all_stopped = False

        if STRICT_SEQUENTIAL:
            self.run_all_mode = 'strict'
            self.stop_btn.show()
            self.hide_btn.show()
            self._run_next_queued_test()
        else:
            self.run_all_mode = 'parallel'
            for label in valid_labels:
                self._run_single_test(label)

    def _run_next_queued_test(self) -> None:
        if self.run_all_stopped or not self.test_queue:
            self._finish_run_all()
            return
        label = self.test_queue.pop(0)
        self._run_single_test(label)

    def stop_run_all(self) -> None:
        self.run_all_stopped = True
        self.append_log("Run All interrupted by user.", "INFO")

    def hide_run_all_controls(self) -> None:
        self.run_all_progress.hide()
        self.stop_btn.hide()
        self.hide_btn.hide()
        self.append_log("Run All controls hidden.", "INFO")

    def _finish_run_all(self) -> None:
        self.run_all_progress.setVisible(False)
        self.test_queue = []
        if self.run_all_mode == 'strict':
            self.stop_btn.hide()
            self.hide_btn.hide()
        self.run_all_mode = None
        self.run_all_stopped = False
        self.append_log("Run All completed.", "INFO")


# ---------------------------
# Entry point
# ---------------------------

def main() -> None:
    global app

    # Ensure DB schema exists
    db_layer.init_users_table_if_needed()

    # Set attributes BEFORE instantiating QApplication
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
