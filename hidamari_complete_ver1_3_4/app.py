import streamlit as st
from config.settings import APP_NAME, APP_VERSION
from db.migrations import init_db
from services.auth_service import login

st.set_page_config(page_title=APP_NAME, page_icon="🌿", layout="wide")
init_db()

st.title(APP_NAME)
st.caption(APP_VERSION)

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user" not in st.session_state:
    st.session_state.user = None

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
if st.sidebar.button("ログアウト"):
    st.session_state.clear()
    st.rerun()

st.success("起動しました。左メニューから dashboard / health input / excretion input を開いてください。")
st.code("facility_id = TEXT\nusers.id = TEXT\nlogin_id = TEXT\nuser_name は互換用のみ", language="text")
