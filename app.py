import streamlit as st
from config.settings import APP_NAME, APP_VERSION, DEFAULT_FACILITY_ID
from db.migrations import init_db
from services.auth_service import login
from views import dashboard, users, health_input, excretion_input, handover

st.set_page_config(page_title=APP_NAME, page_icon="🌿", layout="wide")

# DB初期化
init_db()

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "facility_id" not in st.session_state:
    st.session_state.facility_id = DEFAULT_FACILITY_ID

with st.sidebar:
    st.markdown(f"### {APP_NAME}")
    st.caption(APP_VERSION)

    if not st.session_state.logged_in:
        st.subheader("ログイン")
        login_id = st.text_input("ログインID", value="admin")
        password = st.text_input("パスワード", value="admin", type="password")
        if st.button("ログイン"):
            account = login(login_id, password)
            if account:
                st.session_state.logged_in = True
                st.session_state.staff_name = account.get("staff_name") or account.get("login_id")
                st.session_state.role = account.get("role", "staff")
                st.session_state.facility_id = account.get("facility_id") or DEFAULT_FACILITY_ID
                st.rerun()
            else:
                st.error("ログインIDまたはパスワードが違います。")
        st.stop()

    st.success(f"ログイン中：{st.session_state.get('staff_name', '')}")
    st.divider()
    menu = st.radio(
        "管理者メニュー",
        ["管理者ダッシュボード", "利用者登録", "健康チェック入力", "排泄チェック入力", "申し送り"],
        index=0,
    )
    st.divider()
    if st.button("ログアウト"):
        st.session_state.clear()
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
