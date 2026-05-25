import datetime as dt
import streamlit as st
from services.health_service import add_handover_record


def render():
    st.title("申し送り")
    user = st.session_state.get("user", {})
    with st.form("handover_form"):
        record_date = st.date_input("記録日", value=dt.date.today())
        shift = st.selectbox("勤務帯", ["日勤", "夜勤"])
        content = st.text_area("申し送り内容")
        submitted = st.form_submit_button("登録")
    if submitted:
        if not content.strip():
            st.error("申し送り内容を入力してください。")
            return
        add_handover_record({
            "facility_id": user.get("facility_id", "default"),
            "record_date": str(record_date),
            "shift": shift,
            "content": content.strip(),
            "created_by": user.get("name", ""),
        })
        st.success("申し送りを登録しました。")
