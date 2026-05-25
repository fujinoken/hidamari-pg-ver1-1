import streamlit as st
from db.migrations import init_db
from services.auth_service import login
from config.settings import APP_NAME, APP_VERSION
from views import dashboard, users, health_input, excretion_input, handover

st.set_page_config(page_title=APP_NAME, layout="wide")
init_db()

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "account" not in st.session_state:
    st.session_state.account = None

st.sidebar.title(APP_NAME)
st.sidebar.caption(APP_VERSION)

if not st.session_state.logged_in:
    st.sidebar.subheader("ログイン")
    login_id = st.sidebar.text_input("ログインID", value="admin")
    password = st.sidebar.text_input("パスワード", value="admin", type="password")
    if st.sidebar.button("ログイン"):
        account = login(login_id, password)
        if account:
            st.session_state.logged_in = True
            st.session_state.account = account
            st.rerun()
        else:
            st.sidebar.error("ログインできません。IDまたはパスワードを確認してください。")
    st.title(APP_NAME)
    st.info("左のログイン欄からログインしてください。初期ID/PWは admin / admin です。")
    st.stop()

st.sidebar.success(f"ログイン中：{st.session_state.account.get('staff_name', '職員')}")
st.sidebar.divider()
st.sidebar.subheader("管理者メニュー")
menu = st.sidebar.radio(
    "menu",
    ["管理者ダッシュボード", "利用者登録", "健康チェック入力", "排泄チェック入力", "申し送り"],
    label_visibility="collapsed",
)
st.sidebar.divider()
if st.sidebar.button("ログアウト"):
    st.session_state.logged_in = False
    st.session_state.account = None
    st.rerun()

if menu == "管理者ダッシュボード":
    dashboard.render()
elif menu == "利用者登録":
    users.render()
elif menu == "健康チェック入力":
    health_input.render()
elif menu == "排泄チェック入力":
    excretion_input.render()
elif menu == "申し送り":
    handover.render()
