from sqlalchemy import create_engine
import streamlit as st

def get_engine():
    database_url = st.secrets.get("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL が未設定です")
    return create_engine(database_url, future=True)
