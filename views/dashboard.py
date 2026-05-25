import streamlit as st
import pandas as pd
from services.health_service import list_health_records, list_excretion_records


def render():
    st.header("管理者ダッシュボード")
    st.caption("DB定義統一版 Ver1.3.5")

    st.subheader("健康チェック履歴")
    health_df = pd.DataFrame(list_health_records())
    if health_df.empty:
        st.info("健康チェック記録はまだありません。")
    else:
        st.dataframe(health_df, use_container_width=True)

    st.subheader("排泄チェック履歴")
    excretion_df = pd.DataFrame(list_excretion_records())
    if excretion_df.empty:
        st.info("排泄チェック記録はまだありません。")
    else:
        st.dataframe(excretion_df, use_container_width=True)
