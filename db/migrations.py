from sqlalchemy import text
from config.settings import DEFAULT_FACILITY_ID, DEFAULT_ADMIN_LOGIN_ID, DEFAULT_ADMIN_PASSWORD
from db.database import get_engine, is_postgres, fetch_columns, table_exists

def _exec(conn, sql, params=None):
    conn.execute(text(sql), params or {})

def _add_column(conn, table, column, pg_definition, sqlite_definition=None):
    cols = fetch_columns(conn, table) if table_exists(conn, table) else {}
    if column in cols:
        return
    try:
        if is_postgres(conn.get_bind()):
            _exec(conn, f"ALTER TABLE {table} ADD COLUMN IF NOT EXISTS {column} {pg_definition}")
        else:
            _exec(conn, f"ALTER TABLE {table} ADD COLUMN {column} {sqlite_definition or pg_definition}")
    except Exception:
        pass

def _create_tables(conn):
    pg = is_postgres(conn.get_bind())
    if pg:
        _exec(conn, """
        CREATE TABLE IF NOT EXISTS staff_accounts (
            id TEXT PRIMARY KEY,
            facility_id TEXT NOT NULL DEFAULT 'default',
            login_id TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            staff_name TEXT,
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
            is_active BOOLEAN NOT NULL DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        _exec(conn, """
        CREATE TABLE IF NOT EXISTS health_records (
            id SERIAL PRIMARY KEY,
            facility_id TEXT NOT NULL DEFAULT 'default',
            user_id TEXT NOT NULL,
            record_date TEXT NOT NULL,
            temperature NUMERIC,
            bp_high NUMERIC,
            bp_low NUMERIC,
            pulse NUMERIC,
            spo2 NUMERIC,
            weight NUMERIC,
            meal_rate NUMERIC,
            memo TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        _exec(conn, """
        CREATE TABLE IF NOT EXISTS excretion_records (
            id SERIAL PRIMARY KEY,
            facility_id TEXT NOT NULL DEFAULT 'default',
            user_id TEXT,
            record_date TEXT NOT NULL,
            bowel_movement TEXT,
            urination TEXT,
            memo TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        _exec(conn, """
        CREATE TABLE IF NOT EXISTS handover_records (
            id SERIAL PRIMARY KEY,
            facility_id TEXT NOT NULL DEFAULT 'default',
            record_date TEXT NOT NULL,
            shift_type TEXT,
            content TEXT,
            staff_name TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
    else:
        _exec(conn, """
        CREATE TABLE IF NOT EXISTS staff_accounts (
            id TEXT PRIMARY KEY,
            facility_id TEXT NOT NULL DEFAULT 'default',
            login_id TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            staff_name TEXT,
            role TEXT NOT NULL DEFAULT 'staff',
            is_active INTEGER NOT NULL DEFAULT 1,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """)
        _exec(conn, """
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            facility_id TEXT NOT NULL DEFAULT 'default',
            user_code TEXT,
            user_name TEXT NOT NULL,
            is_active INTEGER NOT NULL DEFAULT 1,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """)
        _exec(conn, """
        CREATE TABLE IF NOT EXISTS health_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
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
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """)
        _exec(conn, """
        CREATE TABLE IF NOT EXISTS excretion_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            facility_id TEXT NOT NULL DEFAULT 'default',
            user_id TEXT,
            record_date TEXT NOT NULL,
            bowel_movement TEXT,
            urination TEXT,
            memo TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """)
        _exec(conn, """
        CREATE TABLE IF NOT EXISTS handover_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            facility_id TEXT NOT NULL DEFAULT 'default',
            record_date TEXT NOT NULL,
            shift_type TEXT,
            content TEXT,
            staff_name TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """)

def _normalize_existing_tables(conn):
    if table_exists(conn, "staff_accounts"):
        for col, pg_def, sqlite_def in [
            ("facility_id", "TEXT DEFAULT 'default'", None),
            ("login_id", "TEXT", None),
            ("password", "TEXT", None),
            ("staff_name", "TEXT", None),
            ("role", "TEXT DEFAULT 'staff'", None),
            ("is_active", "BOOLEAN DEFAULT TRUE", "INTEGER DEFAULT 1"),
            ("created_at", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP", "TEXT DEFAULT CURRENT_TIMESTAMP"),
        ]:
            _add_column(conn, "staff_accounts", col, pg_def, sqlite_def)

    if table_exists(conn, "users"):
        for col, pg_def, sqlite_def in [
            ("facility_id", "TEXT DEFAULT 'default'", None),
            ("user_code", "TEXT", None),
            ("user_name", "TEXT", None),
            ("is_active", "BOOLEAN DEFAULT TRUE", "INTEGER DEFAULT 1"),
            ("created_at", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP", "TEXT DEFAULT CURRENT_TIMESTAMP"),
        ]:
            _add_column(conn, "users", col, pg_def, sqlite_def)

    if table_exists(conn, "health_records"):
        for col, pg_def, sqlite_def in [
            ("facility_id", "TEXT DEFAULT 'default'", None),
            ("user_id", "TEXT", None),
            ("record_date", "TEXT", None),
            ("temperature", "NUMERIC", "REAL"),
            ("bp_high", "NUMERIC", "REAL"),
            ("bp_low", "NUMERIC", "REAL"),
            ("pulse", "NUMERIC", "REAL"),
            ("spo2", "NUMERIC", "REAL"),
            ("weight", "NUMERIC", "REAL"),
            ("meal_rate", "NUMERIC", "REAL"),
            ("memo", "TEXT", None),
            ("created_at", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP", "TEXT DEFAULT CURRENT_TIMESTAMP"),
            ("updated_at", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP", "TEXT DEFAULT CURRENT_TIMESTAMP"),
        ]:
            _add_column(conn, "health_records", col, pg_def, sqlite_def)

        copy_pairs = [
            ("blood_pressure_high", "bp_high"),
            ("blood_pressure_low", "bp_low"),
            ("blood_pressure_upper", "bp_high"),
            ("blood_pressure_lower", "bp_low"),
            ("high_bp", "bp_high"),
            ("low_bp", "bp_low"),
            ("meal_intake", "meal_rate"),
            ("meal_percent", "meal_rate"),
        ]
        for old, new in copy_pairs:
            try:
                _exec(conn, f"UPDATE health_records SET {new}=COALESCE({new}, {old}) WHERE {old} IS NOT NULL")
            except Exception:
                pass

    if table_exists(conn, "excretion_records"):
        for col, pg_def, sqlite_def in [
            ("facility_id", "TEXT DEFAULT 'default'", None),
            ("user_id", "TEXT", None),
            ("record_date", "TEXT", None),
            ("bowel_movement", "TEXT", None),
            ("urination", "TEXT", None),
            ("memo", "TEXT", None),
            ("created_at", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP", "TEXT DEFAULT CURRENT_TIMESTAMP"),
        ]:
            _add_column(conn, "excretion_records", col, pg_def, sqlite_def)

    if table_exists(conn, "handover_records"):
        for col, pg_def, sqlite_def in [
            ("facility_id", "TEXT DEFAULT 'default'", None),
            ("record_date", "TEXT", None),
            ("shift_type", "TEXT", None),
            ("content", "TEXT", None),
            ("staff_name", "TEXT", None),
            ("created_at", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP", "TEXT DEFAULT CURRENT_TIMESTAMP"),
        ]:
            _add_column(conn, "handover_records", col, pg_def, sqlite_def)

def _ensure_admin(conn):
    cols = fetch_columns(conn, "staff_accounts")
    id_type = (cols.get("id") or "").lower()

    try:
        _exec(conn, """
            UPDATE staff_accounts
            SET password=:password,
                staff_name=:staff_name,
                role='admin',
                is_active=TRUE,
                facility_id=:facility_id
            WHERE login_id=:login_id
        """, {
            "password": DEFAULT_ADMIN_PASSWORD,
            "staff_name": "管理者",
            "facility_id": DEFAULT_FACILITY_ID,
            "login_id": DEFAULT_ADMIN_LOGIN_ID,
        })
    except Exception:
        pass

    exists = conn.execute(text("SELECT COUNT(*) FROM staff_accounts WHERE login_id=:login_id"), {"login_id": DEFAULT_ADMIN_LOGIN_ID}).scalar()
    if exists:
        return

    if "int" in id_type:
        active_value = True if is_postgres(conn.get_bind()) else 1
        _exec(conn, """
            INSERT INTO staff_accounts (id, facility_id, login_id, password, staff_name, role, is_active)
            VALUES (
                COALESCE((SELECT MAX(id) + 1 FROM staff_accounts), 1),
                :facility_id, :login_id, :password, :staff_name, 'admin', :is_active
            )
        """, {
            "facility_id": DEFAULT_FACILITY_ID,
            "login_id": DEFAULT_ADMIN_LOGIN_ID,
            "password": DEFAULT_ADMIN_PASSWORD,
            "staff_name": "管理者",
            "is_active": active_value,
        })
    else:
        _exec(conn, """
            INSERT INTO staff_accounts (id, facility_id, login_id, password, staff_name, role, is_active)
            VALUES (:id, :facility_id, :login_id, :password, :staff_name, 'admin', :is_active)
        """, {
            "id": DEFAULT_ADMIN_LOGIN_ID,
            "facility_id": DEFAULT_FACILITY_ID,
            "login_id": DEFAULT_ADMIN_LOGIN_ID,
            "password": DEFAULT_ADMIN_PASSWORD,
            "staff_name": "管理者",
            "is_active": True if is_postgres(conn.get_bind()) else 1,
        })

def init_db():
    engine = get_engine()
    with engine.begin() as conn:
        _create_tables(conn)
        _normalize_existing_tables(conn)
        _ensure_admin(conn)
    return engine

def schema_report():
    engine = get_engine()
    tables = ["staff_accounts", "users", "health_records", "excretion_records", "handover_records"]
    result = {}
    with engine.connect() as conn:
        for table in tables:
            if table_exists(conn, table):
                result[table] = fetch_columns(conn, table)
            else:
                result[table] = {"ERROR": "table not found"}
    return result
