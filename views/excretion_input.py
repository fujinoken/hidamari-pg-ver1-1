from __future__ import annotations
from datetime import date
import streamlit as st
from sqlalchemy import insert
from db.migrations import get_engine
from db.schema import excretion_records
from services.health_service import list_users

def render():
    st.title("排泄チェック入力")
    users_df = list_users(active_only=True)
    if users_df.empty:
        st.warning("利用者が登録されていません。")
        return
    options = {f'{r["user_code"]}｜{r["user_name"]}｜{r.get("room") or ""}': int(r["id"]) for _, r in users_df.iterrows()}
    with st.form("excretion_form"):
        record_date = st.date_input("記録日", value=date.today())
        user = st.selectbox("利用者", list(options.keys()))
        c1, c2 = st.columns(2)
        stool_count = c1.number_input("排便回数", min_value=0, max_value=20, value=0)
        urine_count = c2.number_input("排尿回数", min_value=0, max_value=30, value=0)
        memo = st.text_area("メモ")
        staff_name = st.text_input("記入者名", value=st.session_state.get("staff_name", ""))
        if st.form_submit_button("登録", type="primary"):
            with get_engine().begin() as conn:
                conn.execute(insert(excretion_records).values(record_date=record_date, user_id=options[user], stool_count=int(stool_count), urine_count=int(urine_count), memo=memo or None, staff_name=staff_name or None))
            st.success("排泄チェックを登録しました。")
            st.rerun()
