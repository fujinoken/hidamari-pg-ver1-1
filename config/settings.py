import os
import streamlit as st

APP_NAME = "ひだまり健康チェック管理システム"
APP_VERSION = "Ver1.3.11 型不一致修正版"

DEFAULT_ADMIN_ID = "admin"
DEFAULT_ADMIN_PASSWORD = "admin"
DEFAULT_FACILITY_ID = "default"

def get_database_url() -> str:
    """
    Streamlit secrets の DATABASE_URL / database_url を優先。
    なければローカルSQLiteで動作。
    """
    try:
        if "DATABASE_URL" in st.secrets:
            return st.secrets["DATABASE_URL"]
        if "database_url" in st.secrets:
            return st.secrets["database_url"]
        if "connections" in st.secrets and "postgresql" in st.secrets["connections"]:
            return st.secrets["connections"]["postgresql"]["url"]
    except Exception:
        pass

    return os.environ.get("DATABASE_URL", "sqlite:///hidamari.db")
