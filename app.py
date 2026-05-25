import streamlit as st
from db.migrations import init_db
from services.auth_service import login, ensure_session_defaults
from config.settings import APP_NAME, APP_VERSION
from views import dashboard, health_input, excretion_input, handover

st.set_page_config(page_title=APP_NAME, page_icon="🌿", layout="wide")

# DB初期化
init_db()

ensure_session_defaults(st)

st.sidebar.title(APP_NAME)
st.sidebar.caption(APP_VERSION)

if not st.session_state.logged_in:
    st.title(APP_NAME)
    st.subheader("ログイン")
    with st.form("login_form"):
        login_id = st.text_input("ログインID", value="admin")
        password = st.text_input("パスワード", value="admin", type="password")
        submitted = st.form_submit_button("ログイン")
        if submitted:
            user = login(login_id, password)
            if user:
                st.session_state.logged_in = True
                st.session_state.facility_id = user.get("facility_id", "default")
                st.session_state.role = user.get("role", "admin")
                st.session_state.display_name = user.get("display_name", "管理者")
                st.rerun()
            else:
                st.error("ログインIDまたはパスワードが違います。")
    st.stop()

st.sidebar.success(f"ログイン中：{st.session_state.display_name}")
st.sidebar.divider()

menu = st.sidebar.radio(
    "管理者メニュー",
    ["管理者ダッシュボード", "健康チェック入力", "排泄チェック入力", "申し送り"],
)

st.sidebar.divider()
if st.sidebar.button("ログアウト"):
    st.session_state.logged_in = False
    st.rerun()

if menu == "管理者ダッシュボード":
    dashboard.render()
elif menu == "健康チェック入力":
    health_input.render()
elif menu == "排泄チェック入力":
    excretion_input.render()
elif menu == "申し送り":
    handover.render()
