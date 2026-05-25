import streamlit as st
from config.settings import APP_NAME, APP_VERSION
from db.migrations import init_db
from services.auth_service import login
from views import dashboard, health_input, excretion_input, handover

st.set_page_config(page_title=APP_NAME, page_icon="🌿", layout="wide")
init_db()

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user" not in st.session_state:
    st.session_state.user = None

st.title(APP_NAME)
st.caption(APP_VERSION)

if not st.session_state.logged_in:
    st.subheader("ログイン")
    with st.form("login_form"):
        login_id = st.text_input("ログインID", value="admin")
        password = st.text_input("パスワード", type="password", value="admin")
        submitted = st.form_submit_button("ログイン")
    if submitted:
        user = login(login_id, password)
        if user:
            st.session_state.logged_in = True
            st.session_state.user = user
            st.rerun()
        else:
            st.error("ログインIDまたはパスワードが違います。")
    st.info("初期ログイン：ID admin / PW admin")
    st.stop()

user = st.session_state.user
st.sidebar.success(f"ログイン中：{user['display_name']}")
st.sidebar.markdown("---")
st.sidebar.subheader("管理者メニュー")

menu = st.sidebar.radio(
    "表示する画面を選んでください",
    ["管理者ダッシュボード", "健康チェック入力", "排泄チェック入力", "申し送り"],
    label_visibility="collapsed",
)

st.sidebar.markdown("---")
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
