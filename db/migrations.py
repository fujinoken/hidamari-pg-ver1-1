from __future__ import annotations
import os
import streamlit as st
from sqlalchemy import create_engine, select, insert
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

def init_db():
    engine = get_engine()
    metadata.create_all(engine)
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
