from sqlalchemy import text
from db.connection import engine
from config.settings import DEFAULT_ADMIN_LOGIN_ID, DEFAULT_ADMIN_PASSWORD, DEFAULT_FACILITY_ID


def _exec(conn, sql: str, params: dict | None = None):
    conn.execute(text(sql), params or {})


def init_db():
    """Create required tables. Raw SQL only; avoids SQLAlchemy boolean/type mismatch issues."""
    with engine.begin() as conn:
        _exec(conn, """
        CREATE TABLE IF NOT EXISTS staff_accounts (
            id TEXT PRIMARY KEY,
            facility_id TEXT NOT NULL DEFAULT 'default',
            login_id TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            staff_name TEXT NOT NULL DEFAULT '',
            role TEXT NOT NULL DEFAULT 'staff',
            is_active BOOLEAN NOT NULL DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        _exec(conn, """
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            facility_id TEXT NOT NULL DEFAULT 'default',
            user_code TEXT,
            user_name TEXT NOT NULL,
            kana TEXT,
            is_active BOOLEAN NOT NULL DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        _exec(conn, """
        CREATE TABLE IF NOT EXISTS health_records (
            id TEXT PRIMARY KEY,
            facility_id TEXT NOT NULL DEFAULT 'default',
            user_id TEXT NOT NULL,
            record_date TEXT NOT NULL,
            temperature REAL,
            bp_high REAL,
            bp_low REAL,
            pulse REAL,
            spo2 REAL,
            weight REAL,
            meal_rate REAL,
            memo TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(facility_id, user_id, record_date)
        )
        """)
        _exec(conn, """
        CREATE TABLE IF NOT EXISTS excretion_records (
            id TEXT PRIMARY KEY,
            facility_id TEXT NOT NULL DEFAULT 'default',
            user_id TEXT NOT NULL,
            record_date TEXT NOT NULL,
            stool_count INTEGER DEFAULT 0,
            urine_count INTEGER DEFAULT 0,
            memo TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        _exec(conn, """
        CREATE TABLE IF NOT EXISTS handover_records (
            id TEXT PRIMARY KEY,
            facility_id TEXT NOT NULL DEFAULT 'default',
            record_date TEXT NOT NULL,
            shift_type TEXT,
            content TEXT,
            staff_name TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        _exec(conn, """
        INSERT INTO staff_accounts (id, facility_id, login_id, password, staff_name, role, is_active)
        VALUES (:id, :facility_id, :login_id, :password, :staff_name, 'admin', TRUE)
        ON CONFLICT (id) DO UPDATE SET
            login_id = EXCLUDED.login_id,
            password = EXCLUDED.password,
            staff_name = EXCLUDED.staff_name,
            role = 'admin',
            is_active = TRUE
        """, {
            "id": DEFAULT_ADMIN_LOGIN_ID,
            "facility_id": DEFAULT_FACILITY_ID,
            "login_id": DEFAULT_ADMIN_LOGIN_ID,
            "password": DEFAULT_ADMIN_PASSWORD,
            "staff_name": "管理者",
        })
