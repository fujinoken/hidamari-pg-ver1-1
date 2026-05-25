import streamlit as st
from db.migrations import init_db
from services.auth_service import login, logout
from config.settings import APP_NAME, APP_VERSION
from views import dashboard, user_manage, health_input, excretion_input, handover, db_check

st.set_page_config(page_title=APP_NAME, layout="wide")

try:
    init_db()
except Exception as e:
    st.error("DB初期化でエラーが発生しました。")
    st.exception(e)
    st.stop()

st.sidebar.title(APP_NAME)
st.sidebar.caption(APP_VERSION)

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.sidebar.subheader("ログイン")
    login_id = st.sidebar.text_input("ログインID", value="admin")
    password = st.sidebar.text_input("パスワード", type="password", value="admin")
    if st.sidebar.button("ログイン"):
        account = login(login_id, password)
        if account:
            st.session_state.logged_in = True
            st.session_state.account = account
            st.session_state.facility_id = account.get("facility_id", "default")
            st.session_state.staff_name = account.get("staff_name", "管理者")
            st.session_state.role = account.get("role", "admin")
            st.rerun()
        else:
            st.error("ログインIDまたはパスワードが違います。")
    st.stop()

st.sidebar.success(f"ログイン中：{st.session_state.get('staff_name', '')}")
st.sidebar.divider()

menu_items = ["管理者ダッシュボード", "利用者登録", "健康チェック入力", "排泄チェック入力", "申し送り"]
if st.session_state.get("role") == "admin":
    menu_items.append("DB確認")

menu = st.sidebar.radio("管理者メニュー", menu_items)

if st.sidebar.button("ログアウト"):
    logout(st)
    st.rerun()

try:
    if menu == "管理者ダッシュボード":
        dashboard.render()
    elif menu == "利用者登録":
        user_manage.render()
    elif menu == "健康チェック入力":
        health_input.render()
    elif menu == "排泄チェック入力":
        excretion_input.render()
    elif menu == "申し送り":
        handover.render()
    elif menu == "DB確認":
        db_check.render()
except Exception as e:
    st.error("画面表示中にエラーが発生しました。")
    st.exception(e)
