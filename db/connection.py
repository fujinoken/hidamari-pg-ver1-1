import os
import streamlit as st
from sqlalchemy import create_engine

def get_database_url() -> str:
    # Streamlit Cloud secrets 優先
    try:
        if "DATABASE_URL" in st.secrets:
            return st.secrets["DATABASE_URL"]
    except Exception:
        pass

    # 環境変数
    url = os.getenv("DATABASE_URL")
    if url:
        return url

    # ローカル確認用
    return "sqlite:///hidamari_local.db"

def get_engine():
    url = get_database_url()
    connect_args = {}
    if url.startswith("sqlite"):
        connect_args = {"check_same_thread": False}
    return create_engine(url, pool_pre_ping=True, future=True, connect_args=connect_args)
