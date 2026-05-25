import streamlit as st
from config.settings import APP_NAME
from db.migrations import init_db
from services.auth_service import authenticate
from pages import dashboard, health_input, excretion_input

st.set_page_config(page_title=APP_NAME, page_icon="🌿", layout="wide")

try:
    init_db()
except Exception as e:
    st.error(f"DB初期化エラー: {e}")
    st.stop()

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user" not in st.session_state:
    st.session_state.user = None

st.sidebar.title("app")

if not st.session_state.logged_in:
    st.title(APP_NAME)
    st.caption("DB定義統一版 Ver1.3.4")
    login_id = st.text_input("ログインID", value="admin")
    password = st.text_input("パスワード", type="password", value="admin")
    if st.button("ログイン"):
        user = authenticate(login_id, password)
        if user:
            st.session_state.logged_in = True
            st.session_state.user = user
            st.rerun()
        else:
            st.error("ログインIDまたはパスワードが違います。")
    st.info("初期ID：admin / 初期PW：admin")
    st.stop()

user = st.session_state.user
st.sidebar.caption(user.get("display_name", "user"))
menu = st.sidebar.radio(
    "menu",
    ["dashboard", "health input", "excretion input", "handover"],
)

if st.sidebar.button("ログアウト"):
    st.session_state.logged_in = False
    st.session_state.user = None
    st.rerun()

if menu == "dashboard":
    dashboard.render(user)
elif menu == "health input":
    health_input.render(user)
elif menu == "excretion input":
    excretion_input.render(user)
else:
    st.title("handover")
    st.info("申し送り機能は次段階で追加できます。まずはDB定義統一版の安定起動を優先しています。")
