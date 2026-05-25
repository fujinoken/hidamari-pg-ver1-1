from datetime import date
import streamlit as st
from services.health_service import today_input_status, list_health_records
from services.excretion_service import list_excretion_records

def render():
    st.title("管理者ダッシュボード")
    st.caption("DB安定版・健康チェックCRUD対応")

    st.subheader("今日の健康チェック入力状況")
    status = today_input_status(date.today())
    if status.empty:
        st.info("利用者がまだ登録されていません。")
    else:
        st.dataframe(status, use_container_width=True, hide_index=True)

    st.subheader("健康チェック履歴")
    df = list_health_records(limit=10)
    if df.empty:
        st.info("健康チェック記録はまだありません。")
    else:
        st.dataframe(df, use_container_width=True, hide_index=True)

    st.subheader("排泄チェック履歴")
    ex = list_excretion_records(limit=10)
    if ex.empty:
        st.info("排泄チェック記録はまだありません。")
    else:
        st.dataframe(ex, use_container_width=True, hide_index=True)
