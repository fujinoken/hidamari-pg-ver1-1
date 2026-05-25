import streamlit as st
import pandas as pd
from services.health_service import create_user, list_users

def render():
    st.title("利用者登録")
    fid = st.session_state.get("facility_id", "default")

    with st.form("user_form"):
        user_name = st.text_input("利用者名")
        user_code = st.text_input("利用者コード（任意）")
        submitted = st.form_submit_button("登録")
        if submitted:
            if not user_name.strip():
                st.warning("利用者名を入力してください。")
            else:
                create_user(user_name.strip(), user_code.strip(), fid)
                st.success("利用者を登録しました。")
                st.rerun()

    st.subheader("利用者一覧")
    rows = list_users(fid, active_only=False)
    if rows:
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    else:
        st.info("利用者はまだ登録されていません。")
