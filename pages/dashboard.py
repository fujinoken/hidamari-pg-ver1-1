
from __future__ import annotations
import streamlit as st
from services.health_service import search_health_records, latest_weight_days
from services.excretion_service import search_excretion_records
from services.handover_service import search_handovers
from utils.time_utils import today_jst

def render():
    st.header("ダッシュボード")
    st.caption("今日の入力状況と、次に見ることを静かに確認します。")
    today = today_jst()
    h = search_health_records(start_date=today, end_date=today)
    e = search_excretion_records(start_date=today, end_date=today)
    ho = search_handovers(start_date=today, end_date=today)
    c1,c2,c3 = st.columns(3)
    c1.metric("健康記録", len(h))
    c2.metric("排泄記録", len(e))
    c3.metric("申し送り", len(ho))
    st.subheader("14日以上体重未測定")
    st.info("未測定を責める表示ではなく、次回確認の目安です。")
    df = latest_weight_days()
    if not df.empty:
        st.dataframe(df, use_container_width=True, hide_index=True)
