import streamlit as st
from services.health_service import create_user, list_users


def render():
    st.title("利用者登録")
    with st.form("user_form"):
        user_name = st.text_input("利用者名")
        user_code = st.text_input("利用者コード 任意")
        kana = st.text_input("ふりがな 任意")
        submitted = st.form_submit_button("登録")
    if submitted:
        try:
            create_user(user_name, user_code, kana)
            st.success("利用者を登録しました。")
            st.rerun()
        except Exception as e:
            st.error(f"登録エラー: {e}")
    st.subheader("利用者一覧")
    df = list_users(active_only=False)
    if df.empty:
        st.info("利用者はまだ登録されていません。")
    else:
        st.dataframe(df, use_container_width=True, hide_index=True)
