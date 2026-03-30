# nirix_desktop/db.py
"""
Created on Tue Dec  9 09:20:17 2025

@author: Sri.Sakthivel
"""

import logging
from typing import Optional, Dict, List

import mysql.connector
from mysql.connector import Error
import bcrypt

from . import config as app_config

logger = logging.getLogger(__name__)


# -------------------------------------------------------------------
# DB configuration
# -------------------------------------------------------------------

DB_CONFIG = {
    "host": "127.0.0.1",      # TODO: set to your MySQL host
    "user": "nirix_user",     # TODO: set to your MySQL user
    "password": "journey@123!", # TODO: set to your MySQL password
    "database": "nirix_diagnostics",   # TODO: set to your MySQL DB
    "port": 3306,
}


def get_connection():
    return mysql.connector.connect(
        host=DB_CONFIG["host"],
        user=DB_CONFIG["user"],
        password=DB_CONFIG["password"],
        database=DB_CONFIG["database"],
        port=DB_CONFIG.get("port", 3306),
    )


def init_users_table_if_needed() -> None:
    """
    Create users table if it does not exist.

    This schema is intentionally simple and matches what the UI needs:
    - name, emp_id, email, pin_hash, theme, created_at
    """
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                user_id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(120) NOT NULL,
                emp_id VARCHAR(50) NOT NULL,
                email VARCHAR(120) UNIQUE NOT NULL,
                pin_hash VARCHAR(255) NOT NULL,
                theme VARCHAR(10) DEFAULT 'light',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """
        )
        conn.commit()
        cur.close()
        conn.close()
        logger.info("Users table is ready in MySQL.")
    except Error as e:
        logger.error(f"Error creating users table: {e}")


# -------------------------------------------------------------------
# PIN hashing helpers
# -------------------------------------------------------------------

def hash_pin(pin: str) -> bytes:
    return bcrypt.hashpw(pin.encode("utf-8"), bcrypt.gensalt())


def check_pin(pin: str, pin_hash: bytes) -> bool:
    try:
        return bcrypt.checkpw(pin.encode("utf-8"), pin_hash)
    except Exception:
        return False


# -------------------------------------------------------------------
# CRUD helpers
# -------------------------------------------------------------------

def get_user_by_email(email: str) -> Optional[Dict]:
    try:
        conn = get_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT * FROM users WHERE email=%s", (email,))
        row = cur.fetchone()
        cur.close()
        conn.close()
        return row
    except Error as e:
        logger.error(f"Error fetching user by email: {e}")
        return None


def create_user(name: str, empid: str, email: str, pin: str) -> None:
    """
    Create a new user. Raises ValueError if email already exists.
    """
    existing = get_user_by_email(email)
    if existing:
        raise ValueError("A user with this email already exists.")

    try:
        conn = get_connection()
        cur = conn.cursor()
        pin_hash = hash_pin(pin)
        cur.execute(
            "INSERT INTO users (name, emp_id, email, pin_hash) VALUES (%s, %s, %s, %s)",
            (name, empid, email, pin_hash),
        )
        conn.commit()
        cur.close()
        conn.close()
        logger.info(f"Created user in DB: {email}")
    except Error as e:
        logger.error(f"Error creating user: {e}")
        raise


def get_all_users_for_ui() -> List[List[str]]:
    """
    For compatibility with the old Excel-based code that expected
    rows like [Name, EmpID, Email, Approver, PIN].

    We do not expose the real PIN from DB; we return '****' and empty approver.
    """
    rows: List[List[str]] = []
    try:
        conn = get_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT name, emp_id, email FROM users")
        for r in cur.fetchall():
            rows.append([r["name"], r["emp_id"], r["email"], "", "****"])
        cur.close()
        conn.close()
    except Error as e:
        logger.error(f"Error fetching users: {e}")
    return rows
