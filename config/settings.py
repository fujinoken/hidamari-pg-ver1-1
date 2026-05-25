from __future__ import annotations

import os
import streamlit as st

APP_NAME = "ひだまり健康チェック管理システム"
APP_VERSION = "Ver1.1 PostgreSQL 新設計版"
DEFAULT_FACILITY_NAME = "ひだまり"


def get_database_url() -> str:
    """DATABASE_URLを Streamlit secrets または環境変数から取得する。"""
    try:
        url = st.secrets.get("DATABASE_URL", "")
        if url:
            return str(url)
    except Exception:
        pass
    return os.getenv("DATABASE_URL", "")


def require_database_url() -> str:
    url = get_database_url()
    if not url:
        raise RuntimeError(
            "DATABASE_URL が未設定です。Streamlit Cloud の Secrets に DATABASE_URL を設定してください。"
        )
    return url
