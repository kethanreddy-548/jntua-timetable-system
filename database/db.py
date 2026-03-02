"""
Database Layer — SQLite
Tables: users, departments, faculty, subjects, timetable_slots, room_assignments
"""
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "jntua.db")

def get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    conn = get_conn()
    c = conn.cursor()

    # ── USERS ────────────────────────────────────────────────
    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        username    TEXT UNIQUE NOT NULL,
        password    TEXT NOT NULL,
        role        TEXT NOT NULL CHECK(role IN ('superadmin','hod')),
        dept_id     INTEGER REFERENCES departments(id),
        full_name   TEXT,
        email       TEXT,
        is_active   INTEGER DEFAULT 1,
        last_login  TEXT,
        created_at  TEXT DEFAULT (datetime('now'))
    )""")

    # ── LOGIN ATTEMPTS (rate limiting) ───────────────────────
    c.execute("""
    CREATE TABLE IF NOT EXISTS login_attempts (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        username    TEXT,
        ip          TEXT,
        success     INTEGER,
        attempted_at TEXT DEFAULT (datetime('now'))
    )""")

    # ── DEPARTMENTS ──────────────────────────────────────────
    c.execute("""
    CREATE TABLE IF NOT EXISTS departments (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        code        TEXT UNIQUE NOT NULL,
        name        TEXT NOT NULL,
        hod_name    TEXT,
        created_at  TEXT DEFAULT (datetime('now'))
    )""")

    # ── FACULTY ──────────────────────────────────────────────
    c.execute("""
    CREATE TABLE IF NOT EXISTS faculty (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        emp_id          TEXT UNIQUE NOT NULL,
        name            TEXT NOT NULL,
        designation     TEXT,
        dept_id         INTEGER NOT NULL REFERENCES departments(id),
        email           TEXT,
        max_theory_hrs  INTEGER DEFAULT 3,
        max_lab_hrs     INTEGER DEFAULT 6,
        is_active       INTEGER DEFAULT 1,
        created_at      TEXT DEFAULT (datetime('now'))
    )""")

    # ── SUBJECTS ─────────────────────────────────────────────
    c.execute("""
    CREATE TABLE IF NOT EXISTS subjects (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        code        TEXT NOT NULL,
        name        TEXT NOT NULL,
        dept_id     INTEGER NOT NULL REFERENCES departments(id),
        year        INTEGER NOT NULL CHECK(year IN (1,2,3,4)),
        semester    INTEGER NOT NULL CHECK(semester IN (1,2)),
        regulation  TEXT NOT NULL CHECK(regulation IN ('R23','R21')),
        type        TEXT NOT NULL CHECK(type IN ('theory','lab')),
        hours_week  INTEGER NOT NULL,
        credits     REAL NOT NULL,
        is_active   INTEGER DEFAULT 1,
        created_at  TEXT DEFAULT (datetime('now')),
        UNIQUE(code, regulation)
    )""")

    # ── SUBJECT-FACULTY MAPPING ──────────────────────────────
    c.execute("""
    CREATE TABLE IF NOT EXISTS subject_faculty (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        subject_id  INTEGER NOT NULL REFERENCES subjects(id),
        faculty_id  INTEGER NOT NULL REFERENCES faculty(id),
        role        TEXT DEFAULT 'primary' CHECK(role IN ('primary','lab_incharge','lab_assistant')),
        UNIQUE(subject_id, faculty_id, role)
    )""")

    # ── GENERATED TIMETABLE SLOTS ────────────────────────────
    c.execute("""
    CREATE TABLE IF NOT EXISTS timetable_slots (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        branch      TEXT NOT NULL,
        year        INTEGER NOT NULL,
        semester    INTEGER NOT NULL,
        regulation  TEXT NOT NULL,
        day         TEXT NOT NULL,
        time_slot   TEXT NOT NULL,
        subject_id  INTEGER REFERENCES subjects(id),
        faculty_id  INTEGER REFERENCES faculty(id),
        room        TEXT,
        slot_type   TEXT,
        generated_at TEXT DEFAULT (datetime('now'))
    )""")

    # ── ROOM ASSIGNMENTS (admin-managed) ─────────────────────
    # One classroom + one lab per branch per year per semester
    c.execute("""
    CREATE TABLE IF NOT EXISTS room_assignments (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        year        INTEGER NOT NULL CHECK(year IN (1,2,3,4)),
        semester    INTEGER NOT NULL CHECK(semester IN (1,2)),
        branch      TEXT NOT NULL,
        classroom   TEXT NOT NULL,
        lab_room    TEXT NOT NULL,
        updated_at  TEXT DEFAULT (datetime('now')),
        UNIQUE(year, semester, branch)
    )""")

    conn.commit()
    conn.close()

# ── HELPERS ──────────────────────────────────────────────────
def fetchall(query, params=()):
    conn = get_conn()
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def fetchone(query, params=()):
    conn = get_conn()
    row = conn.execute(query, params).fetchone()
    conn.close()
    return dict(row) if row else None

def execute(query, params=()):
    conn = get_conn()
    cursor = conn.execute(query, params)
    conn.commit()
    last_id = cursor.lastrowid
    conn.close()
    return last_id

def executemany(query, params_list):
    conn = get_conn()
    conn.executemany(query, params_list)
    conn.commit()
    conn.close()