from __future__ import annotations
from datetime import date
import streamlit as st
from sqlalchemy import insert
from db.migrations import get_engine
from db.schema import handovers
from services.health_service import list_handovers

def render():
    st.title("申し送り")
    with st.form("handover_form"):
        record_date = st.date_input("日付", value=date.today())
        shift = st.selectbox("勤務帯", ["日勤", "夜勤"])
        title = st.text_input("タイトル")
        body = st.text_area("内容")
        staff_name = st.text_input("記入者名", value=st.session_state.get("staff_name", ""))
        if st.form_submit_button("登録", type="primary"):
            with get_engine().begin() as conn:
                conn.execute(insert(handovers).values(record_date=record_date, shift=shift, title=title or None, body=body or None, staff_name=staff_name or None))
            st.success("申し送りを登録しました。")
            st.rerun()
    st.divider()
    st.subheader("申し送り履歴")
    df = list_handovers()
    if df.empty:
        st.info("申し送りはまだありません。")
    else:
        st.dataframe(df, use_container_width=True, hide_index=True)
