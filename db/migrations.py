import os
import streamlit as st
from sqlalchemy import create_engine, text
from config.settings import DEFAULT_ADMIN_ID, DEFAULT_ADMIN_PASSWORD, DEFAULT_ADMIN_NAME, DEFAULT_FACILITY_ID
from db.schema import metadata


def get_database_url() -> str:
    url = None
    try:
        url = st.secrets.get("DATABASE_URL")
    except Exception:
        url = None
    url = url or os.environ.get("DATABASE_URL") or "sqlite:///hidamari.db"
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql+psycopg2://", 1)
    elif url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+psycopg2://", 1)
    return url


_ENGINE = None


def get_engine():
    global _ENGINE
    if _ENGINE is None:
        _ENGINE = create_engine(get_database_url(), pool_pre_ping=True, future=True)
    return _ENGINE


def init_db():
    engine = get_engine()
    metadata.create_all(engine)
    with engine.begin() as conn:
        exists = conn.execute(
            text("SELECT id FROM users WHERE login_id = :login_id LIMIT 1"),
            {"login_id": DEFAULT_ADMIN_ID},
        ).first()
        if not exists:
            conn.execute(
                text("""
                INSERT INTO users (id, facility_id, login_id, password, name, role)
                VALUES (:id, :facility_id, :login_id, :password, :name, :role)
                """),
                {
                    "id": "admin",
                    "facility_id": DEFAULT_FACILITY_ID,
                    "login_id": DEFAULT_ADMIN_ID,
                    "password": DEFAULT_ADMIN_PASSWORD,
                    "name": DEFAULT_ADMIN_NAME,
                    "role": "admin",
                },
            )
