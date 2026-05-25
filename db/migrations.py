from sqlalchemy import text
from db.connection import get_engine
from config.settings import DEFAULT_ADMIN_LOGIN_ID, DEFAULT_ADMIN_PASSWORD, DEFAULT_FACILITY_ID, DEFAULT_FACILITY_NAME

def _is_postgres(conn) -> bool:
    return conn.dialect.name == "postgresql"

def _exec(conn, sql: str, params: dict | None = None):
    return conn.execute(text(sql), params or {})

def _column_exists(conn, table_name: str, column_name: str) -> bool:
    if _is_postgres(conn):
        sql = """
        SELECT COUNT(*) FROM information_schema.columns
        WHERE table_name = :table_name AND column_name = :column_name
        """
        return (_exec(conn, sql, {"table_name": table_name, "column_name": column_name}).scalar() or 0) > 0
    else:
        rows = _exec(conn, f"PRAGMA table_info({table_name})").fetchall()
        return any(r[1] == column_name for r in rows)

def _add_column_if_missing(conn, table_name: str, column_name: str, column_def: str):
    if not _column_exists(conn, table_name, column_name):
        _exec(conn, f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_def}")

def _table_exists(conn, table_name: str) -> bool:
    if _is_postgres(conn):
        sql = "SELECT to_regclass(:name)"
        return _exec(conn, sql, {"name": f"public.{table_name}"}).scalar() is not None
    else:
        sql = "SELECT name FROM sqlite_master WHERE type='table' AND name=:name"
        return _exec(conn, sql, {"name": table_name}).first() is not None

def init_db():
    """
    重要：
    PostgreSQL/Neonに古いテーブルが残っていても落ちないように、
    CREATE TABLE IF NOT EXISTS + 不足列追加 + 文字列日付比較に統一しています。
    user_id/dateの型不一致を避けるため、検索時はCASTを使います。
    """
    engine = get_engine()
    with engine.begin() as conn:
        if _is_postgres(conn):
            str_type = "TEXT"
            num_type = "DOUBLE PRECISION"
            id_type = "TEXT PRIMARY KEY"
            now_default = "DEFAULT CURRENT_TIMESTAMP"
        else:
            str_type = "TEXT"
            num_type = "REAL"
            id_type = "TEXT PRIMARY KEY"
            now_default = "DEFAULT CURRENT_TIMESTAMP"

        _exec(conn, f"""
        CREATE TABLE IF NOT EXISTS facilities (
            id {id_type},
            facility_name {str_type} NOT NULL,
            created_at {str_type} {now_default}
        )
        """)

        _exec(conn, f"""
        CREATE TABLE IF NOT EXISTS staff_accounts (
            id {id_type},
            facility_id {str_type} NOT NULL,
            login_id {str_type} UNIQUE NOT NULL,
            password {str_type} NOT NULL,
            staff_name {str_type},
            role {str_type} DEFAULT 'staff',
            is_active BOOLEAN DEFAULT TRUE,
            created_at {str_type} {now_default}
        )
        """)

        _exec(conn, f"""
        CREATE TABLE IF NOT EXISTS users (
            id {id_type},
            facility_id {str_type} NOT NULL,
            user_code {str_type},
            user_name {str_type} NOT NULL,
            room {str_type},
            is_active BOOLEAN DEFAULT TRUE,
            created_at {str_type} {now_default}
        )
        """)

        _exec(conn, f"""
        CREATE TABLE IF NOT EXISTS health_records (
            id {id_type},
            facility_id {str_type} NOT NULL,
            user_id {str_type} NOT NULL,
            record_date {str_type} NOT NULL,
            temperature {num_type},
            blood_pressure_high {num_type},
            blood_pressure_low {num_type},
            pulse {num_type},
            spo2 {num_type},
            weight {num_type},
            meal_rate {num_type},
            memo {str_type},
            created_at {str_type} {now_default},
            updated_at {str_type} {now_default}
        )
        """)

        _exec(conn, f"""
        CREATE TABLE IF NOT EXISTS excretion_records (
            id {id_type},
            facility_id {str_type} NOT NULL,
            user_id {str_type} NOT NULL,
            record_date {str_type} NOT NULL,
            bowel_count INTEGER DEFAULT 0,
            urine_count INTEGER DEFAULT 0,
            memo {str_type},
            created_at {str_type} {now_default}
        )
        """)

        _exec(conn, f"""
        CREATE TABLE IF NOT EXISTS handover_records (
            id {id_type},
            facility_id {str_type} NOT NULL,
            record_date {str_type} NOT NULL,
            shift {str_type},
            content {str_type},
            important BOOLEAN DEFAULT FALSE,
            created_at {str_type} {now_default}
        )
        """)

        # 既存DB補正
        for col, coldef in [
            ("facility_id", str_type), ("user_code", str_type), ("user_name", str_type),
            ("room", str_type), ("is_active", "BOOLEAN DEFAULT TRUE"), ("created_at", f"{str_type} {now_default}")
        ]:
            _add_column_if_missing(conn, "users", col, coldef)

        for col, coldef in [
            ("facility_id", str_type), ("user_id", str_type), ("record_date", str_type),
            ("temperature", num_type), ("blood_pressure_high", num_type), ("blood_pressure_low", num_type),
            ("pulse", num_type), ("spo2", num_type), ("weight", num_type), ("meal_rate", num_type),
            ("memo", str_type), ("created_at", f"{str_type} {now_default}"), ("updated_at", f"{str_type} {now_default}")
        ]:
            _add_column_if_missing(conn, "health_records", col, coldef)

        for col, coldef in [
            ("facility_id", str_type), ("login_id", str_type), ("password", str_type),
            ("staff_name", str_type), ("role", str_type), ("is_active", "BOOLEAN DEFAULT TRUE")
        ]:
            _add_column_if_missing(conn, "staff_accounts", col, coldef)

        # 初期施設
        if _is_postgres(conn):
            _exec(conn, """
            INSERT INTO facilities (id, facility_name)
            VALUES (:id, :name)
            ON CONFLICT (id) DO NOTHING
            """, {"id": DEFAULT_FACILITY_ID, "name": DEFAULT_FACILITY_NAME})
            _exec(conn, """
            INSERT INTO staff_accounts (id, facility_id, login_id, password, staff_name, role, is_active)
            VALUES ('admin', :facility_id, :login_id, :password, '管理者', 'admin', TRUE)
            ON CONFLICT (login_id) DO NOTHING
            """, {"facility_id": DEFAULT_FACILITY_ID, "login_id": DEFAULT_ADMIN_LOGIN_ID, "password": DEFAULT_ADMIN_PASSWORD})
        else:
            _exec(conn, """
            INSERT OR IGNORE INTO facilities (id, facility_name)
            VALUES (:id, :name)
            """, {"id": DEFAULT_FACILITY_ID, "name": DEFAULT_FACILITY_NAME})
            _exec(conn, """
            INSERT OR IGNORE INTO staff_accounts (id, facility_id, login_id, password, staff_name, role, is_active)
            VALUES ('admin', :facility_id, :login_id, :password, '管理者', 'admin', 1)
            """, {"facility_id": DEFAULT_FACILITY_ID, "login_id": DEFAULT_ADMIN_LOGIN_ID, "password": DEFAULT_ADMIN_PASSWORD})
