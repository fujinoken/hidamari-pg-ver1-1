from __future__ import annotations
import streamlit as st
from services.health_service import get_health_records, get_excretion_records

def render(user: dict):
    st.title("管理者ダッシュボード")
    st.caption("DB定義統一版 Ver1.3.4")

    facility_id = user.get("facility_id", "default")

    st.subheader("健康チェック履歴")
    df = get_health_records(facility_id=facility_id, limit=50)
    if df.empty:
        st.info("健康チェック記録はまだありません。")
    else:
        st.dataframe(df, use_container_width=True)

    st.subheader("排泄チェック履歴")
    ex = get_excretion_records(facility_id=facility_id, limit=50)
    if ex.empty:
        st.info("排泄チェック記録はまだありません。")
    else:
        st.dataframe(ex, use_container_width=True)
