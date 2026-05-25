import datetime as dt
import streamlit as st
from services.health_service import today_input_status, list_health_records


def render():
    st.title("管理者ダッシュボード")
    st.caption("DB安定版・健康チェックCRUD対応")
    today = dt.date.today().isoformat()
    st.subheader("今日の健康チェック入力状況")
    try:
        status = today_input_status(today)
        if status.empty:
            st.info("利用者登録がまだありません。左メニューの『利用者登録』から登録してください。")
        else:
            st.dataframe(status, use_container_width=True, hide_index=True)
    except Exception as e:
        st.error(f"入力状況の取得でエラー: {e}")

    st.subheader("直近の健康チェック履歴")
    try:
        df = list_health_records()
        if df.empty:
            st.info("健康チェック記録はまだありません。")
        else:
            st.dataframe(df.head(20), use_container_width=True, hide_index=True)
    except Exception as e:
        st.error(f"履歴取得でエラー: {e}")
