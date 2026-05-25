
import streamlit as st
from config.settings import APP_NAME, APP_VERSION
from db.migrations import init_db

# ページ読込
from pages import (
    dashboard,
    health_input,
    excretion_input,
    handover_input,
)

# =====================================
# 初期化
# =====================================
st.set_page_config(
    page_title=APP_NAME,
    page_icon="🏥",
    layout="wide",
)

# DB初期化
try:
    init_db(seed=True)
except Exception as e:
    st.error(f"DB初期化エラー: {e}")
    st.stop()

# =====================================
# セッション
# =====================================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = True

if "user_name" not in st.session_state:
    st.session_state.user_name = "admin"

if "role" not in st.session_state:
    st.session_state.role = "admin"

# =====================================
# サイドバー
# =====================================
with st.sidebar:
    st.title(APP_NAME)
    st.caption(f"Ver {APP_VERSION}")

    st.divider()

    st.write(f"ログイン中: {st.session_state.user_name}")
    st.write(f"権限: {st.session_state.role}")

    st.divider()

    menu = st.radio(
        "メニュー",
        [
            "ダッシュボード",
            "健康チェック入力",
            "排泄チェック入力",
            "申し送り",
        ],
    )

    st.divider()

    if st.button("ログアウト"):
        st.session_state.logged_in = False
        st.rerun()

# =====================================
# メイン画面
# =====================================
st.title(APP_NAME)

if menu == "ダッシュボード":
    dashboard.render()

elif menu == "健康チェック入力":
    health_input.render()

elif menu == "排泄チェック入力":
    excretion_input.render()

elif menu == "申し送り":
    handover_input.render()
