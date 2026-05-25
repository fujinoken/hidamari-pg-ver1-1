from datetime import date
import streamlit as st
from services.health_service import add_handover_record


def render():
    st.title("申し送り")
    with st.form("handover_form"):
        record_date = st.date_input("日付", value=date.today())
        shift = st.selectbox("勤務帯", ["日勤", "夜勤"])
        content = st.text_area("申し送り内容", height=180)
        staff_name = st.text_input("職員名", value=st.session_state.get("user_name", ""))
        submitted = st.form_submit_button("登録")

    if submitted:
        add_handover_record({
            "record_date": record_date,
            "shift": shift,
            "content": content,
            "staff_name": staff_name,
        })
        st.success("申し送りを登録しました。")
