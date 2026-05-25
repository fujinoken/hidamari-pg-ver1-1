from __future__ import annotations
import os
import streamlit as st
from sqlalchemy import create_engine, select, insert, text, inspect
from db.schema import metadata, staff_accounts
from config.settings import DEFAULT_ADMIN_LOGIN_ID, DEFAULT_ADMIN_PASSWORD, DEFAULT_ADMIN_NAME

@st.cache_resource
def get_engine():
    db_url = None
    try:
        db_url = st.secrets.get("DATABASE_URL")
    except Exception:
        db_url = None
    if not db_url:
        db_url = os.environ.get("DATABASE_URL")
    if not db_url:
        db_url = "sqlite:///hidamari.db"
    return create_engine(db_url, future=True, pool_pre_ping=True)

def _dialect_name(engine) -> str:
    try:
        return engine.dialect.name
    except Exception:
        return ""

def _column_exists(conn, table_name: str, column_name: str) -> bool:
    inspector = inspect(conn)
    try:
        return column_name in [c["name"] for c in inspector.get_columns(table_name)]
    except Exception:
        return False

def _add_column_if_missing(conn, table_name: str, column_name: str, ddl_type: str):
    if _column_exists(conn, table_name, column_name):
        return
    dialect = _dialect_name(conn.engine)
    if dialect == "postgresql":
        conn.execute(text(f'ALTER TABLE {table_name} ADD COLUMN IF NOT EXISTS {column_name} {ddl_type}'))
    else:
        conn.execute(text(f'ALTER TABLE {table_name} ADD COLUMN {column_name} {ddl_type}'))

def ensure_schema_compatibility(engine):
    """既存DBを壊さず、Ver1.3.10で必要な列を追加する。
    metadata.create_all は既存テーブルの列追加をしないため、ここで補完する。
    """
    with engine.begin() as conn:
        dialect = _dialect_name(engine)

        # staff_accounts
        for name, typ in [
            ("login_id", "VARCHAR(100)"), ("password", "VARCHAR(255)"),
            ("staff_name", "VARCHAR(100)"), ("role", "VARCHAR(50)"),
            ("is_active", "BOOLEAN"), ("created_at", "TIMESTAMP"),
        ]:
            _add_column_if_missing(conn, "staff_accounts", name, typ)

        # users
        for name, typ in [
            ("user_code", "VARCHAR(50)"), ("user_name", "VARCHAR(100)"),
            ("room", "VARCHAR(50)"), ("birth_date", "DATE"),
            ("gender", "VARCHAR(20)"), ("is_active", "BOOLEAN"),
            ("memo", "TEXT"), ("created_at", "TIMESTAMP"), ("updated_at", "TIMESTAMP"),
        ]:
            _add_column_if_missing(conn, "users", name, typ)

        # health_records
        for name, typ in [
            ("record_date", "DATE"), ("user_id", "INTEGER"),
            ("temperature", "FLOAT"), ("blood_pressure_high", "INTEGER"),
            ("blood_pressure_low", "INTEGER"), ("pulse", "INTEGER"),
            ("spo2", "INTEGER"), ("weight", "FLOAT"),
            ("meal_rate", "INTEGER"), ("water_amount", "INTEGER"),
            ("family_memo", "TEXT"), ("staff_memo", "TEXT"),
            ("staff_name", "VARCHAR(100)"), ("created_at", "TIMESTAMP"), ("updated_at", "TIMESTAMP"),
        ]:
            _add_column_if_missing(conn, "health_records", name, typ)

        # excretion_records
        for name, typ in [
            ("record_date", "DATE"), ("user_id", "INTEGER"),
            ("stool_count", "INTEGER"), ("urine_count", "INTEGER"),
            ("memo", "TEXT"), ("staff_name", "VARCHAR(100)"), ("created_at", "TIMESTAMP"),
        ]:
            _add_column_if_missing(conn, "excretion_records", name, typ)

        # handovers
        for name, typ in [
            ("record_date", "DATE"), ("shift", "VARCHAR(20)"),
            ("title", "VARCHAR(200)"), ("body", "TEXT"),
            ("staff_name", "VARCHAR(100)"), ("created_at", "TIMESTAMP"),
        ]:
            _add_column_if_missing(conn, "handovers", name, typ)

        # 既存データのNULL補完（PostgreSQL / SQLite 両対応）
        if dialect == "postgresql":
            conn.execute(text("UPDATE users SET user_code = COALESCE(user_code, CAST(id AS TEXT)) WHERE user_code IS NULL OR user_code = ''"))
            conn.execute(text("UPDATE users SET user_name = COALESCE(user_name, name, login_id, '利用者' || CAST(id AS TEXT)) WHERE user_name IS NULL OR user_name = ''"))
            conn.execute(text("UPDATE users SET is_active = TRUE WHERE is_active IS NULL"))
            conn.execute(text("UPDATE users SET created_at = NOW() WHERE created_at IS NULL"))
            conn.execute(text("UPDATE users SET updated_at = NOW() WHERE updated_at IS NULL"))
            conn.execute(text("UPDATE staff_accounts SET is_active = TRUE WHERE is_active IS NULL"))
            conn.execute(text("UPDATE staff_accounts SET created_at = NOW() WHERE created_at IS NULL"))
        else:
            conn.execute(text("UPDATE users SET user_code = COALESCE(user_code, CAST(id AS TEXT)) WHERE user_code IS NULL OR user_code = ''"))
            # SQLiteには存在しない列参照で落ちる場合があるため、最小補完
            conn.execute(text("UPDATE users SET user_name = COALESCE(user_name, '利用者' || CAST(id AS TEXT)) WHERE user_name IS NULL OR user_name = ''"))
            conn.execute(text("UPDATE users SET is_active = 1 WHERE is_active IS NULL"))
            conn.execute(text("UPDATE users SET created_at = CURRENT_TIMESTAMP WHERE created_at IS NULL"))
            conn.execute(text("UPDATE users SET updated_at = CURRENT_TIMESTAMP WHERE updated_at IS NULL"))
            conn.execute(text("UPDATE staff_accounts SET is_active = 1 WHERE is_active IS NULL"))
            conn.execute(text("UPDATE staff_accounts SET created_at = CURRENT_TIMESTAMP WHERE created_at IS NULL"))

def init_db():
    engine = get_engine()
    metadata.create_all(engine)
    ensure_schema_compatibility(engine)
    with engine.begin() as conn:
        exists = conn.execute(select(staff_accounts.c.id).where(staff_accounts.c.login_id == DEFAULT_ADMIN_LOGIN_ID)).first()
        if not exists:
            conn.execute(insert(staff_accounts).values(
                login_id=DEFAULT_ADMIN_LOGIN_ID,
                password=DEFAULT_ADMIN_PASSWORD,
                staff_name=DEFAULT_ADMIN_NAME,
                role="admin",
                is_active=True,
            ))
