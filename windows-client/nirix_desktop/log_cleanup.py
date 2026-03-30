# nirix_desktop/log_cleanup.py
"""
Created on Tue Dec  9 09:22:01 2025

@author: Sri.Sakthivel
"""

import os
import time
import logging
from typing import Optional

logger = logging.getLogger(__name__)


def cleanup_old_logs(log_folder: str, keep_days: int = 7) -> None:
    """
    Delete log files older than keep_days in the given folder.
    Only affects regular files, not directories.
    """
    if not os.path.isdir(log_folder):
        return

    now = time.time()
    cutoff = now - keep_days * 24 * 3600

    deleted = 0
    for name in os.listdir(log_folder):
        path = os.path.join(log_folder, name)
        if not os.path.isfile(path):
            continue
        try:
            mtime = os.path.getmtime(path)
        except OSError:
            continue
        if mtime < cutoff:
            try:
                os.remove(path)
                deleted += 1
            except OSError as e:
                logger.warning(f"Failed to remove old log {path}: {e}")

    if deleted > 0:
        logger.info(f"Cleaned {deleted} old log file(s) from {log_folder}.")
