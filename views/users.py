import streamlit as st
import pandas as pd
from services.health_service import add_user, list_users, deactivate_user

def render():
    facility_id = st.session_state["facility_id"]
    st.title("利用者登録")

    with st.form("add_user_form", clear_on_submit=True):
        st.subheader("新規利用者登録")
        user_name = st.text_input("利用者名")
        user_code = st.text_input("利用者コード（任意）")
        room = st.text_input("居室・部屋番号（任意）")
        submitted = st.form_submit_button("登録")
        if submitted:
            if not user_name.strip():
                st.error("利用者名を入力してください。")
            else:
                add_user(facility_id, user_name.strip(), user_code.strip(), room.strip())
                st.success("利用者を登録しました。")
                st.rerun()

    st.subheader("利用者一覧")
    users = list_users(facility_id, active_only=True)
    if users:
        st.dataframe(pd.DataFrame(users), use_container_width=True, hide_index=True)
        options = {f"{u['user_name']}（{u.get('room','')}）": u["id"] for u in users}
        target = st.selectbox("利用停止にする利用者", ["選択してください"] + list(options.keys()))
        if target != "選択してください":
            if st.button("この利用者を利用停止にする", type="secondary"):
                deactivate_user(options[target])
                st.success("利用停止にしました。")
                st.rerun()
    else:
        st.info("利用者はまだ登録されていません。")
