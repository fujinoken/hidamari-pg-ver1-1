from datetime import date
import streamlit as st
from sqlalchemy import text
from db.migrations import get_engine
from config.settings import DEFAULT_FACILITY_ID

def render():
    st.title("申し送り")
    with st.form("handover_form"):
        record_date = st.date_input("日付", value=date.today())
        shift = st.selectbox("勤務帯", ["日勤", "夜勤"])
        content = st.text_area("申し送り内容")
        submitted = st.form_submit_button("登録")
        if submitted:
            engine = get_engine()
            with engine.begin() as conn:
                conn.execute(text("""
                    INSERT INTO handover_records
                    (facility_id, record_date, shift, content, created_by)
                    VALUES (:facility_id, :record_date, :shift, :content, :created_by)
                """), {
                    "facility_id": DEFAULT_FACILITY_ID,
                    "record_date": record_date,
                    "shift": shift,
                    "content": content,
                    "created_by": st.session_state.get("user_name", "管理者"),
                })
            st.success("申し送りを登録しました。")
            st.rerun()

    st.subheader("申し送り履歴")
    engine = get_engine()
    with engine.begin() as conn:
        rows = conn.execute(text("""
            SELECT record_date, shift, content, created_by
            FROM handover_records
            ORDER BY record_date DESC, id DESC
            LIMIT 100
        """)).mappings().all()
    if rows:
        st.dataframe([dict(r) for r in rows], use_container_width=True, hide_index=True)
    else:
        st.info("申し送り記録はまだありません。")
