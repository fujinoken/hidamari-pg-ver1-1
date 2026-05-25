import streamlit as st
from services.health_service import list_health_records, list_excretion_records, list_handover_records, to_dataframe
from config.settings import APP_VERSION


def render():
    st.caption(f"{APP_VERSION}｜メニュー整理・DB安定版")
    st.title("管理者ダッシュボード")
    st.caption("DB定義統一版")

    st.subheader("健康チェック履歴")
    health = list_health_records(20)
    if health:
        st.dataframe(to_dataframe(health), use_container_width=True)
    else:
        st.info("健康チェック記録はまだありません。")

    st.subheader("排泄チェック履歴")
    excretion = list_excretion_records(20)
    if excretion:
        st.dataframe(to_dataframe(excretion), use_container_width=True)
    else:
        st.info("排泄チェック記録はまだありません。")

    st.subheader("申し送り履歴")
    handover = list_handover_records(20)
    if handover:
        st.dataframe(to_dataframe(handover), use_container_width=True)
    else:
        st.info("申し送り記録はまだありません。")
