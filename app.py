from __future__ import annotations

import streamlit as st

from config.settings import APP_NAME, APP_VERSION
from db.migrations import init_db
from services.auth_service import authenticate, change_password
from services.audit_service import add_audit_log
from components.ui import apply_yohaku_style, app_sidebar
from pages import dashboard, health_input, excretion_input, handover, admin


st.set_page_config(
    page_title=APP_NAME,
    page_icon="☀️",
    layout="wide",
    initial_sidebar_state="expanded",
)


def hide_streamlit_page_nav():
    st.markdown(
        """
        <style>
        [data-testid="stSidebarNav"] {
            display: none !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


apply_yohaku_style()
hide_streamlit_page_nav()


def ensure_bootstrap():
    try:
        init_db(seed=True)
    except Exception as e:
        st.error("データベース初期化に失敗しました。DATABASE_URL とPostgreSQL接続を確認してください。")
        st.exception(e)
        st.stop()


def login_screen():
    st.title(APP_NAME)
    st.caption(APP_VERSION)
    st.info("PostgreSQL新設計版です。初期IDは kanri / staff、初期PWは rui です。初回ログイン後に変更してください。")

    with st.form("login_form"):
        login_id = st.text_input("ログインID")
        password = st.text_input("パスワード", type="password")
        submitted = st.form_submit_button("ログイン", type="primary", use_container_width=True)

    if submitted:
        user = authenticate(login_id, password)
        if not user:
            st.error("ログインできません。IDまたはパスワードを確認してください。")
            add_audit_log(login_id, "", "ログイン失敗", "staff_accounts", summary="認証失敗")
            return

        st.session_state["current_user"] = user
        add_audit_log(
            user.get("login_id"),
            user.get("role"),
            "ログイン成功",
            "staff_accounts",
            user.get("id"),
            user.get("display_name"),
        )
        st.rerun()


def password_change_screen(user: dict):
    st.title("初回パスワード変更")
    st.warning("初期パスワードのまま通常画面へ進めません。")

    with st.form("password_change"):
        new_pw = st.text_input("新しいパスワード", type="password")
        new_pw2 = st.text_input("新しいパスワード（確認）", type="password")
        submitted = st.form_submit_button("パスワードを変更", type="primary", use_container_width=True)

    if submitted:
        if new_pw != new_pw2:
            st.error("確認用パスワードが一致しません。")
            return

        try:
            change_password(user["id"], new_pw)
            add_audit_log(
                user.get("login_id"),
                user.get("role"),
                "初回パスワード変更",
                "staff_accounts",
                user.get("id"),
            )
            st.session_state["current_user"]["must_change_password"] = False
            st.success("変更しました。")
            st.rerun()
        except Exception as e:
            st.error(str(e))


def main():
    ensure_bootstrap()

    user = st.session_state.get("current_user")
    if not user:
        login_screen()
        return

    if user.get("must_change_password"):
        password_change_screen(user)
        return

    app_sidebar()

    st.sidebar.write(f"ログイン：{user.get('display_name')}（{user.get('role')}）")

    if st.sidebar.button("ログアウト", use_container_width=True):
        st.session_state.pop("current_user", None)
        st.rerun()

    menus = [
        "ダッシュボード",
        "健康チェック",
        "排泄チェック",
        "業務全体申し送り",
    ]

    if user.get("role") == "admin":
        menus.append("管理者画面")

    selected = st.sidebar.radio("メニュー", menus)

    if selected == "ダッシュボード":
        dashboard.render()
    elif selected == "健康チェック":
        health_input.render(user)
    elif selected == "排泄チェック":
        excretion_input.render(user)
    elif selected == "業務全体申し送り":
        handover.render(user)
    elif selected == "管理者画面":
        admin.render(user)


if __name__ == "__main__":
    main()
