from __future__ import annotations

import os
import streamlit as st

APP_NAME = "ひだまり健康チェック管理システム"
APP_VERSION = "Ver1.3.1 PostgreSQL DB定義統一版"

# DB定義統一方針
# - facility_id は TEXT
# - users.id は TEXT
# - login_id は TEXT
# - user_name は互換用の任意列として残す
DEFAULT_FACILITY_ID = "facility_default"
DEFAULT_FACILITY_NAME = "ひだまり"


def get_database_url() -> str:
    """
    Streamlit Cloud Secrets または環境変数から DATABASE_URL を取得する。
    """
    url = ""
    try:
        url = st.secrets.get("DATABASE_URL", "")
    except Exception:
        url = ""

    if not url:
        url = os.environ.get("DATABASE_URL", "")

    return str(url).strip()


def require_database_url() -> str:
    url = get_database_url()
    if not url:
        raise RuntimeError(
            "DATABASE_URL が未設定です。Streamlit Cloud の Secrets に DATABASE_URL を設定してください。"
        )
    return url
