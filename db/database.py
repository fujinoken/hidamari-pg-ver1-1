from sqlalchemy import create_engine, text
import streamlit as st

def get_database_url():
    try:
        return st.secrets["DATABASE_URL"]
    except Exception:
        return "sqlite:///hidamari.db"

def get_engine():
    return create_engine(get_database_url(), future=True, pool_pre_ping=True)

def is_postgres(engine_or_bind=None):
    engine_or_bind = engine_or_bind or get_engine()
    return engine_or_bind.url.get_backend_name().startswith("postgresql")

def fetch_columns(conn, table_name: str):
    bind = conn.get_bind()
    if bind.url.get_backend_name().startswith("postgresql"):
        rows = conn.execute(text("""
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_name = :table_name
        """), {"table_name": table_name}).mappings().all()
        return {r["column_name"]: r["data_type"] for r in rows}
    rows = conn.execute(text(f"PRAGMA table_info({table_name})")).mappings().all()
    return {r["name"]: r["type"] for r in rows}

def table_exists(conn, table_name: str) -> bool:
    bind = conn.get_bind()
    if bind.url.get_backend_name().startswith("postgresql"):
        return conn.execute(text("""
            SELECT EXISTS (
                SELECT 1 FROM information_schema.tables
                WHERE table_name = :table_name
            )
        """), {"table_name": table_name}).scalar()
    row = conn.execute(text("""
        SELECT name FROM sqlite_master
        WHERE type='table' AND name=:table_name
    """), {"table_name": table_name}).first()
    return row is not None
