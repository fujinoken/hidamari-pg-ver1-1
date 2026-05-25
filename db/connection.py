import os
import streamlit as st
from sqlalchemy import create_engine


def get_database_url() -> str:
    try:
        url = st.secrets.get("DATABASE_URL", "")
    except Exception:
        url = ""
    if not url:
        url = os.getenv("DATABASE_URL", "")
    if not url:
        # local fallback
        return "sqlite:///hidamari_local.db"
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql+psycopg2://", 1)
    elif url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+psycopg2://", 1)
    return url


engine = create_engine(get_database_url(), pool_pre_ping=True, future=True)
