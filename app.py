import streamlit as st
from config.settings import APP_NAME, APP_VERSION
from db.migrations import init_db
from services.auth_service import login
from views import dashboard, health_input, excretion_input, handover

st.set_page_config(page_title=APP_NAME, page_icon="🌻", layout="wide")

# 起動時に必ずDBとテーブルを作成する
init_db()

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_name" not in st.session_state:
    st.session_state.user_name = ""
if "role" not in st.session_state:
    st.session_state.role = ""

st.sidebar.title("ひだまり健康チェック")
st.sidebar.caption(APP_VERSION)

if not st.session_state.logged_in:
    st.title(APP_NAME)
    st.subheader("ログイン")
    login_id = st.text_input("ログインID", value="admin")
    password = st.text_input("パスワード", type="password", value="admin")
    if st.button("ログイン"):
        user = login(login_id, password)
        if user:
            st.session_state.logged_in = True
            st.session_state.user_name = user["name"]
            st.session_state.role = user["role"]
            st.rerun()
        else:
            st.error("ログインIDまたはパスワードが違います。")
    st.info("初期ID：admin / 初期パスワード：admin")
    st.stop()

st.sidebar.success(f"ログイン中：{st.session_state.user_name}")
st.sidebar.divider()
st.sidebar.subheader("管理者メニュー")
menu = st.sidebar.radio(
    "menu",
    ["管理者ダッシュボード", "健康チェック入力", "排泄チェック入力", "申し送り"],
    label_visibility="collapsed",
)

st.sidebar.divider()
if st.sidebar.button("ログアウト"):
    st.session_state.clear()
    st.rerun()

if menu == "管理者ダッシュボード":
    dashboard.render()
elif menu == "健康チェック入力":
    health_input.render()
elif menu == "排泄チェック入力":
    excretion_input.render()
elif menu == "申し送り":
    handover.render()
