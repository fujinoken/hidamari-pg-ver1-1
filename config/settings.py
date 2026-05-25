
from __future__ import annotations
import os
import streamlit as st

APP_NAME = "ひだまり健康チェック管理システム"
APP_VERSION = "Ver1.3 PostgreSQL 商品化基盤版"

DEFAULT_FACILITY_ID = 1
DEFAULT_FACILITY_NAME = "ひだまり"

def get_database_url() -> str:
    value = ""
    try:
        value = st.secrets.get("DATABASE_URL", "")
    except Exception:
        value = ""
    value = value or os.environ.get("DATABASE_URL", "")
    return str(value).strip()

def require_database_url() -> str:
    url = get_database_url()
    if not url:
        raise RuntimeError("DATABASE_URL が未設定です。Streamlit Cloud の Secrets に DATABASE_URL を設定してください。")
    return url
