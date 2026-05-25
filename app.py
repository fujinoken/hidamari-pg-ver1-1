from __future__ import annotations
import streamlit as st
from config.settings import APP_NAME, APP_VERSION
from db.migrations import init_db
from services.auth_service import login
from views import dashboard, users, health_input, excretion_input, handover

st.set_page_config(page_title=APP_NAME, page_icon="🌿", layout="wide")
init_db()

def show_login():
    st.title(APP_NAME)
    st.caption(APP_VERSION)
    st.subheader("ログイン")
    with st.form("login_form"):
        login_id = st.text_input("ログインID", value="admin")
        password = st.text_input("パスワード", type="password", value="admin")
        submitted = st.form_submit_button("ログイン", type="primary")
        if submitted:
            account = login(login_id, password)
            if account:
                st.session_state["logged_in"] = True
                st.session_state["staff_name"] = account.get("staff_name", "")
                st.session_state["role"] = account.get("role", "staff")
                st.rerun()
            else:
                st.error("ログインIDまたはパスワードが違います。")

def sidebar_menu():
    st.sidebar.title(APP_NAME)
    st.sidebar.caption(APP_VERSION)
    if st.session_state.get("logged_in"):
        st.sidebar.success(f"ログイン中：{st.session_state.get('staff_name', '')}")
    st.sidebar.divider()
    st.sidebar.subheader("管理者メニュー")
    menu = st.sidebar.radio("メニュー", ["管理者ダッシュボード", "利用者登録", "健康チェック入力", "排泄チェック入力", "申し送り"], label_visibility="collapsed")
    st.sidebar.divider()
    if st.sidebar.button("ログアウト"):
        for k in ["logged_in", "staff_name", "role"]:
            st.session_state.pop(k, None)
        st.rerun()
    return menu

if not st.session_state.get("logged_in"):
    show_login()
else:
    menu = sidebar_menu()
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
