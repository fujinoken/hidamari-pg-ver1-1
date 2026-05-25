from __future__ import annotations

import streamlit as st
import pandas as pd
from services.health_service import list_health_records, weight_unmeasured_over
from services.excretion_service import list_excretion_records
from services.handover_service import list_handovers
from components.ui import header


def render():
    header("ダッシュボード", "今日の入力状況と、次に見ることを静かに確認します。")

    c1, c2, c3 = st.columns(3)
    health = list_health_records(limit=50)
    excretion = list_excretion_records(limit=50)
    handovers = list_handovers(limit=20)
    c1.metric("健康記録", len(health))
    c2.metric("排泄記録", len(excretion))
    c3.metric("申し送り", len(handovers))

    st.subheader("14日以上体重未測定")
    weight_rows = weight_unmeasured_over(14)
    if weight_rows:
        st.info("未測定を責める表示ではなく、次回確認の目安です。")
        st.dataframe(pd.DataFrame(weight_rows), use_container_width=True, hide_index=True)
    else:
        st.success("14日以上体重未測定の利用者はいません。")

    st.subheader("最近の申し送り")
    if handovers:
        st.dataframe(pd.DataFrame(handovers), use_container_width=True, hide_index=True)
    else:
        st.caption("申し送りはまだありません。")
