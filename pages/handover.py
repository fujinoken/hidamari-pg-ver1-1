from __future__ import annotations

import streamlit as st
import pandas as pd
from services.handover_service import create_handover, list_handovers
from services.audit_service import add_audit_log
from utils.time_utils import today_jst
from components.ui import header


def render(current_user: dict):
    header("業務全体申し送り", "事実・気づき・次に見ることを分け、責めない共有にします。")
    with st.form("handover_form"):
        record_date = st.date_input("日付", value=today_jst())
        shift = st.selectbox("勤務帯", ["日勤", "夜勤"])
        writer = st.text_input("記入者", value=current_user.get("display_name", ""))
        fact_text = st.text_area("事実", placeholder="実際に起きたこと・見たこと")
        notice_text = st.text_area("気づき", placeholder="普段との違い、気になったこと")
        next_watch_text = st.text_area("次に見ること", placeholder="次の勤務者が確認するとよいこと")
        priority = st.selectbox("優先度", ["通常", "観察", "注意", "至急"])
        status = st.selectbox("状態", ["観察継続", "一旦様子を見る", "対応中", "完了"])
        submitted = st.form_submit_button("申し送りを保存", type="primary", use_container_width=True)

    if submitted:
        row = create_handover({
            "record_date": record_date,
            "shift": shift,
            "writer": writer,
            "fact_text": fact_text,
            "notice_text": notice_text,
            "next_watch_text": next_watch_text,
            "priority": priority,
            "status": status,
        })
        add_audit_log(current_user.get("login_id"), current_user.get("role"), "申し送り保存", "handover_logs", row.id, f"{record_date} {shift}")
        st.success("保存しました。")
        st.rerun()

    st.subheader("最近の申し送り")
    rows = list_handovers(200)
    if rows:
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
