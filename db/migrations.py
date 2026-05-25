import os
import uuid
from sqlalchemy import create_engine, inspect, text
from db.schema import metadata
from config.settings import DEFAULT_ADMIN_LOGIN_ID, DEFAULT_ADMIN_PASSWORD, DEFAULT_FACILITY_ID

def get_database_url():
    try:
        import streamlit as st
        if "DATABASE_URL" in st.secrets:
            return st.secrets["DATABASE_URL"]
    except Exception:
        pass
    return os.environ.get("DATABASE_URL", "sqlite:///hidamari.db")

def get_engine():
    url = get_database_url()
    kwargs = {}
    if url.startswith("sqlite"):
        kwargs["connect_args"] = {"check_same_thread": False}
    return create_engine(url, future=True, **kwargs)

def _add_column_if_missing(conn, table_name, column_name, column_sql):
    inspector = inspect(conn)
    if table_name not in inspector.get_table_names():
        return
    cols = [c["name"] for c in inspector.get_columns(table_name)]
    if column_name not in cols:
        conn.execute(text(f"ALTER TABLE {table_name} ADD COLUMN {column_sql}"))

def _safe_schema_patch(conn):
    # 既存DBに列不足がある場合のみ補正する。型変更は危険なので、SELECT側でCASTして吸収する。
    patches = [
        ("staff_accounts", "facility_id", "facility_id TEXT DEFAULT 'default'"),
        ("staff_accounts", "display_name", "display_name TEXT DEFAULT '管理者'"),
        ("staff_accounts", "role", "role TEXT DEFAULT 'admin'"),
        ("staff_accounts", "is_active", "is_active BOOLEAN DEFAULT TRUE"),
        ("users", "facility_id", "facility_id TEXT DEFAULT 'default'"),
        ("users", "user_code", "user_code TEXT"),
        ("users", "user_name", "user_name TEXT"),
        ("users", "room", "room TEXT"),
        ("users", "is_active", "is_active BOOLEAN DEFAULT TRUE"),
        ("health_records", "facility_id", "facility_id TEXT DEFAULT 'default'"),
        ("health_records", "user_id", "user_id TEXT"),
        ("health_records", "record_date", "record_date DATE"),
        ("health_records", "temperature", "temperature DOUBLE PRECISION"),
        ("health_records", "blood_pressure_high", "blood_pressure_high DOUBLE PRECISION"),
        ("health_records", "blood_pressure_low", "blood_pressure_low DOUBLE PRECISION"),
        ("health_records", "pulse", "pulse DOUBLE PRECISION"),
        ("health_records", "spo2", "spo2 DOUBLE PRECISION"),
        ("health_records", "weight", "weight DOUBLE PRECISION"),
        ("health_records", "meal_rate", "meal_rate DOUBLE PRECISION"),
        ("health_records", "memo", "memo TEXT"),
        ("health_records", "updated_at", "updated_at TIMESTAMP"),
        ("excretion_records", "facility_id", "facility_id TEXT DEFAULT 'default'"),
        ("excretion_records", "user_id", "user_id TEXT"),
        ("excretion_records", "record_date", "record_date DATE"),
        ("excretion_records", "urination", "urination TEXT"),
        ("excretion_records", "defecation", "defecation TEXT"),
        ("excretion_records", "memo", "memo TEXT"),
        ("handover_records", "facility_id", "facility_id TEXT DEFAULT 'default'"),
        ("handover_records", "record_date", "record_date DATE"),
        ("handover_records", "shift", "shift TEXT"),
        ("handover_records", "content", "content TEXT"),
        ("handover_records", "created_by", "created_by TEXT"),
    ]
    for p in patches:
        try:
            _add_column_if_missing(conn, *p)
        except Exception:
            # 既存DBの方言差や既に存在する場合は止めない
            pass

def init_db():
    engine = get_engine()
    metadata.create_all(engine)
    with engine.begin() as conn:
        _safe_schema_patch(conn)

        # admin 初期作成。既に存在する場合は何もしない。
        exists = conn.execute(
            text("SELECT COUNT(*) FROM staff_accounts WHERE login_id = :login_id"),
            {"login_id": DEFAULT_ADMIN_LOGIN_ID},
        ).scalar() or 0

        if int(exists) == 0:
            conn.execute(
                text("""
                    INSERT INTO staff_accounts
                    (id, facility_id, login_id, password, display_name, role, is_active)
                    VALUES
                    (:id, :facility_id, :login_id, :password, :display_name, :role, :is_active)
                """),
                {
                    "id": str(uuid.uuid4()),
                    "facility_id": DEFAULT_FACILITY_ID,
                    "login_id": DEFAULT_ADMIN_LOGIN_ID,
                    "password": DEFAULT_ADMIN_PASSWORD,
                    "display_name": "管理者",
                    "role": "admin",
                    "is_active": True,
                },
            )
    return engine
