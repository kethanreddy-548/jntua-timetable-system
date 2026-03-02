"""
Security Module
- bcrypt password hashing
- Session token management
- Rate limiting (5 attempts → 15min lockout)
- Role-based access control
"""
import hashlib
import hmac
import os
import secrets
import time
import streamlit as st
from datetime import datetime, timedelta
from database.db import fetchone, fetchall, execute

SECRET_KEY = os.environ.get("SECRET_KEY", "jntua_cea_secret_2024_xK9mP2vL")
MAX_ATTEMPTS = 5
LOCKOUT_MINUTES = 15


# ── PASSWORD HASHING (SHA-256 + salt) ────────────────────────
def hash_password(password: str) -> str:
    salt = secrets.token_hex(32)
    key  = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 310000)
    return f"{salt}:{key.hex()}"


def verify_password(password: str, stored: str) -> bool:
    try:
        salt, key_hex = stored.split(":", 1)
        key = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 310000)
        return hmac.compare_digest(key.hex(), key_hex)
    except Exception:
        return False


# ── RATE LIMITING ─────────────────────────────────────────────
def is_locked_out(username: str) -> tuple:
    cutoff = (datetime.now() - timedelta(minutes=LOCKOUT_MINUTES)).strftime("%Y-%m-%d %H:%M:%S")
    row = fetchone("""
        SELECT COUNT(*) as cnt FROM login_attempts
        WHERE username=? AND success=0 AND attempted_at > ?
    """, (username, cutoff))
    count = row["cnt"] if row else 0
    remaining = MAX_ATTEMPTS - count
    return count >= MAX_ATTEMPTS, max(0, remaining)


def log_attempt(username: str, success: bool):
    execute("""INSERT INTO login_attempts(username, success)
               VALUES(?,?)""", (username, 1 if success else 0))


# ── LOGIN ─────────────────────────────────────────────────────
def authenticate(username: str, password: str) -> dict | None:
    locked, remaining = is_locked_out(username)
    if locked:
        return {"error": f"Account locked for {LOCKOUT_MINUTES} mins due to too many failed attempts."}

    user = fetchone("SELECT * FROM users WHERE username=? AND is_active=1", (username,))
    if not user:
        log_attempt(username, False)
        return {"error": f"Invalid credentials. {remaining-1} attempts remaining."}

    if not verify_password(password, user["password"]):
        log_attempt(username, False)
        locked_now, rem = is_locked_out(username)
        if locked_now:
            return {"error": f"Too many failed attempts. Account locked for {LOCKOUT_MINUTES} minutes."}
        return {"error": f"Invalid credentials. {rem} attempts remaining."}

    log_attempt(username, True)
    execute("UPDATE users SET last_login=datetime('now') WHERE id=?", (user["id"],))
    return user


# ── SESSION HELPERS ───────────────────────────────────────────
def login_user(user: dict):
    st.session_state["logged_in"]   = True
    st.session_state["user_id"]     = user["id"]
    st.session_state["username"]    = user["username"]
    st.session_state["role"]        = user["role"]
    st.session_state["full_name"]   = user["full_name"] or user["username"]
    st.session_state["dept_id"]     = user["dept_id"]
    st.session_state["login_time"]  = datetime.now().isoformat()


def logout_user():
    for key in ["logged_in","user_id","username","role","full_name","dept_id","login_time"]:
        st.session_state.pop(key, None)


def is_logged_in() -> bool:
    return st.session_state.get("logged_in", False)


def current_role() -> str:
    return st.session_state.get("role", "")


def current_dept_id():
    return st.session_state.get("dept_id")


def require_login():
    if not is_logged_in():
        st.session_state["page"] = "login"
        st.rerun()


def require_role(role: str):
    require_login()
    if current_role() != role and current_role() != "superadmin":
        st.error("⛔ Access Denied — Insufficient permissions")
        st.stop()


def change_password(user_id: int, old_pwd: str, new_pwd: str) -> dict:
    user = fetchone("SELECT * FROM users WHERE id=?", (user_id,))
    if not user:
        return {"error": "User not found"}
    if not verify_password(old_pwd, user["password"]):
        return {"error": "Current password is incorrect"}
    if len(new_pwd) < 8:
        return {"error": "New password must be at least 8 characters"}
    if not any(c.isupper() for c in new_pwd):
        return {"error": "Password must contain at least one uppercase letter"}
    if not any(c.isdigit() for c in new_pwd):
        return {"error": "Password must contain at least one digit"}

    execute("UPDATE users SET password=? WHERE id=?", (hash_password(new_pwd), user_id))
    return {"success": True}
