"""
Real User Store — Stage 85-95% of the build path.

SQLite-backed user accounts and sessions. Real password hashing (stdlib
hashlib.pbkdf2_hmac, no new dependency), real session tokens, real
per-user workspace paths. No stub records - every function here either
touches a real database and returns a real result, or raises a real error.
"""
from __future__ import annotations

import hashlib
import os
import secrets
import sqlite3
import time
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "aziz_users.db"
PBKDF2_ITERATIONS = 200_000


def _get_conn(db_path: Path = DB_PATH) -> sqlite3.Connection:
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db(db_path: Path = DB_PATH) -> None:
    """Real schema creation. Safe to call every startup - CREATE TABLE IF NOT EXISTS."""
    conn = _get_conn(db_path)
    try:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                password_salt TEXT NOT NULL,
                created_at REAL NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                token TEXT PRIMARY KEY,
                user_id INTEGER NOT NULL,
                created_at REAL NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        conn.commit()
    finally:
        conn.close()


class UserError(ValueError):
    """Raised for real, expected problems: duplicate username, wrong password, etc."""


def _hash_password(password: str, salt: bytes) -> str:
    return hashlib.pbkdf2_hmac("sha256", password.encode(), salt, PBKDF2_ITERATIONS).hex()


def create_user(username: str, password: str, db_path: Path = DB_PATH) -> int:
    """Real signup: hashes the password for real, inserts a real row. Returns the new user_id."""
    username = username.strip()
    if not username or len(username) < 3:
        raise UserError("username must be at least 3 characters")
    if not password or len(password) < 4:
        raise UserError("password must be at least 4 characters")

    salt = secrets.token_bytes(16)
    password_hash = _hash_password(password, salt)

    conn = _get_conn(db_path)
    try:
        try:
            cur = conn.execute(
                "INSERT INTO users (username, password_hash, password_salt, created_at) VALUES (?, ?, ?, ?)",
                (username, password_hash, salt.hex(), time.time()),
            )
            conn.commit()
            return cur.lastrowid
        except sqlite3.IntegrityError as exc:
            raise UserError(f"username '{username}' is already taken") from exc
    finally:
        conn.close()


def verify_login(username: str, password: str, db_path: Path = DB_PATH) -> int:
    """Real login check: re-hashes the given password with the STORED salt and
    compares against the STORED hash. Returns user_id on success."""
    conn = _get_conn(db_path)
    try:
        row = conn.execute(
            "SELECT id, password_hash, password_salt FROM users WHERE username = ?", (username.strip(),)
        ).fetchone()
    finally:
        conn.close()

    if row is None:
        raise UserError("invalid username or password")

    salt = bytes.fromhex(row["password_salt"])
    candidate_hash = _hash_password(password, salt)
    # secrets.compare_digest avoids timing side-channels on the comparison itself
    if not secrets.compare_digest(candidate_hash, row["password_hash"]):
        raise UserError("invalid username or password")

    return row["id"]


def create_session(user_id: int, db_path: Path = DB_PATH) -> str:
    """Real session: a cryptographically random token, stored server-side."""
    token = secrets.token_urlsafe(32)
    conn = _get_conn(db_path)
    try:
        conn.execute(
            "INSERT INTO sessions (token, user_id, created_at) VALUES (?, ?, ?)",
            (token, user_id, time.time()),
        )
        conn.commit()
    finally:
        conn.close()
    return token


def get_user_id_for_session(token: str, db_path: Path = DB_PATH) -> int | None:
    """Real session lookup. Returns None (not an error) for an unknown/expired token -
    that's an expected, normal case (logged out, cookie cleared, etc.), not a bug."""
    if not token:
        return None
    conn = _get_conn(db_path)
    try:
        row = conn.execute("SELECT user_id FROM sessions WHERE token = ?", (token,)).fetchone()
    finally:
        conn.close()
    return row["user_id"] if row else None


def delete_session(token: str, db_path: Path = DB_PATH) -> None:
    conn = _get_conn(db_path)
    try:
        conn.execute("DELETE FROM sessions WHERE token = ?", (token,))
        conn.commit()
    finally:
        conn.close()


def get_username(user_id: int, db_path: Path = DB_PATH) -> str | None:
    conn = _get_conn(db_path)
    try:
        row = conn.execute("SELECT username FROM users WHERE id = ?", (user_id,)).fetchone()
    finally:
        conn.close()
    return row["username"] if row else None


def user_workspace_dir(user_id: int, base_workspace: Path) -> Path:
    """Real per-user isolation: every user's generated projects live under
    their own numeric folder, never mixed with anyone else's."""
    path = base_workspace / f"user_{user_id}"
    path.mkdir(parents=True, exist_ok=True)
    return path
