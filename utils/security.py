from __future__ import annotations

import binascii
import hashlib
import hmac
import os
import re
import sqlite3
from datetime import datetime
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "patient_history.db"
PBKDF2_ITERATIONS = 260_000


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def hash_registered_password(password: str) -> str:
    salt = os.urandom(16)
    password_hash = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, PBKDF2_ITERATIONS)
    return (
        f"pbkdf2_sha256${PBKDF2_ITERATIONS}$"
        f"{binascii.hexlify(salt).decode('ascii')}$"
        f"{binascii.hexlify(password_hash).decode('ascii')}"
    )


def verify_registered_password(password: str, stored_hash: str) -> bool:
    try:
        algorithm, iterations, salt_hex, hash_hex = stored_hash.split("$", 3)
        if algorithm != "pbkdf2_sha256":
            return False
        salt = binascii.unhexlify(salt_hex)
        expected_hash = binascii.unhexlify(hash_hex)
        actual_hash = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, int(iterations))
        return hmac.compare_digest(actual_hash, expected_hash)
    except (ValueError, binascii.Error):
        return False


def init_user_store() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL,
                username TEXT NOT NULL UNIQUE,
                full_name TEXT NOT NULL,
                role TEXT NOT NULL,
                password_hash TEXT NOT NULL
            )
            """
        )
        conn.commit()


def default_credentials() -> dict[str, str]:
    doctor_password = os.getenv("CVD_DOCTOR_PASSWORD", "doctor123")
    admin_password = os.getenv("CVD_ADMIN_PASSWORD", "admin123")
    return {
        "doctor": hash_password(doctor_password),
        "admin": hash_password(admin_password),
    }


def normalize_username(username: str) -> str:
    return username.strip().lower()


def validate_registration(full_name: str, username: str, password: str, confirm_password: str) -> list[str]:
    errors: list[str] = []
    username = normalize_username(username)
    full_name = full_name.strip()

    if len(full_name) < 2:
        errors.append("Full name is required.")
    if not re.fullmatch(r"[a-z0-9_.-]{3,32}", username):
        errors.append("Username must be 3-32 characters and use only letters, numbers, dots, underscores, or hyphens.")
    if len(password) < 8:
        errors.append("Password must be at least 8 characters.")
    if password != confirm_password:
        errors.append("Passwords do not match.")
    return errors


def create_user(full_name: str, username: str, password: str, role: str = "doctor") -> tuple[bool, str]:
    init_user_store()
    username = normalize_username(username)
    full_name = full_name.strip()
    password_hash = hash_registered_password(password)

    try:
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute(
                """
                INSERT INTO users (created_at, username, full_name, role, password_hash)
                VALUES (?, ?, ?, ?, ?)
                """,
                (datetime.now().isoformat(timespec="seconds"), username, full_name, role, password_hash),
            )
            conn.commit()
    except sqlite3.IntegrityError:
        return False, "This username is already registered."

    return True, "Account created successfully. You can now sign in."


def verify_registered_user(username: str, password: str) -> bool:
    init_user_store()
    username = normalize_username(username)
    with sqlite3.connect(DB_PATH) as conn:
        row = conn.execute("SELECT password_hash FROM users WHERE username = ?", (username,)).fetchone()
    if row is None:
        return False
    return verify_registered_password(password, row[0])


def verify_password(username: str, password: str, credentials: dict[str, str] | None = None) -> bool:
    if verify_registered_user(username, password):
        return True

    credentials = credentials or default_credentials()
    expected_hash = credentials.get(normalize_username(username))
    if not expected_hash:
        return False
    return hmac.compare_digest(hash_password(password), expected_hash)
