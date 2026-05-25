import streamlit as st
from services.health_service import create_user, list_users

def render():
    st.title("利用者登録")

    with st.form("user_create_form"):
        user_name = st.text_input("利用者名")
        room = st.text_input("居室・メモ", placeholder="例：101号室")
        submitted = st.form_submit_button("利用者を登録")
        if submitted:
            try:
                create_user(user_name=user_name, room=room)
                st.success("利用者を登録しました。")
                st.rerun()
            except Exception as e:
                st.error(f"登録できませんでした：{e}")

    st.subheader("利用者一覧")
    users = list_users(active_only=False)
    if users:
        st.dataframe(users, use_container_width=True, hide_index=True)
    else:
        st.info("利用者はまだ登録されていません。")
