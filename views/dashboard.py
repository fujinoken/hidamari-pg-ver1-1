from __future__ import annotations
from datetime import date
import streamlit as st
from services.health_service import list_health_records, list_excretion_records, list_handovers, today_input_status

def render():
    st.title("管理者ダッシュボード")
    st.caption("DB安定版・健康チェックCRUD対応")
    st.subheader("今日の健康チェック入力状況")
    status = today_input_status(date.today())
    if status.empty:
        st.info("利用者が登録されていません。")
    else:
        done = (status["入力状況"] == "入力済み").sum()
        st.metric("入力済み", f"{done}/{len(status)} 名")
        st.dataframe(status, use_container_width=True, hide_index=True)
    st.divider()
    st.subheader("直近の健康チェック履歴")
    h = list_health_records()
    if h.empty:
        st.info("健康チェック記録はまだありません。")
    else:
        cols = ["record_date", "user_name", "temperature", "blood_pressure_high", "blood_pressure_low", "spo2", "meal_rate", "staff_name"]
        st.dataframe(h[cols].head(10), use_container_width=True, hide_index=True)
    st.divider()
    st.subheader("排泄チェック履歴")
    e = list_excretion_records()
    st.info("排泄チェック記録はまだありません。" if e.empty else "排泄チェック記録があります。")
    if not e.empty:
        st.dataframe(e, use_container_width=True, hide_index=True)
    st.subheader("申し送り履歴")
    m = list_handovers()
    st.info("申し送り記録はまだありません。" if m.empty else "申し送り記録があります。")
    if not m.empty:
        st.dataframe(m, use_container_width=True, hide_index=True)
