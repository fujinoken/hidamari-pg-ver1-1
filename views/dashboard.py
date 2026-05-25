import streamlit as st
from services.health_service import list_health_records, list_excretion_records, list_handover_records


def render():
    st.title("管理者ダッシュボード")
    st.caption("DB定義統一版 Ver1.3.6")

    st.subheader("健康チェック履歴")
    try:
        df = list_health_records()
        if df.empty:
            st.info("健康チェック記録はまだありません。")
        else:
            st.dataframe(df, use_container_width=True)
    except Exception as e:
        st.error("健康チェック履歴の読み込みに失敗しました。")
        st.exception(e)

    st.subheader("排泄チェック履歴")
    try:
        df = list_excretion_records()
        if df.empty:
            st.info("排泄チェック記録はまだありません。")
        else:
            st.dataframe(df, use_container_width=True)
    except Exception as e:
        st.error("排泄チェック履歴の読み込みに失敗しました。")
        st.exception(e)

    st.subheader("申し送り履歴")
    try:
        df = list_handover_records()
        if df.empty:
            st.info("申し送り記録はまだありません。")
        else:
            st.dataframe(df, use_container_width=True)
    except Exception as e:
        st.error("申し送り履歴の読み込みに失敗しました。")
        st.exception(e)
