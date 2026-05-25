import datetime as dt
import streamlit as st
from services.health_service import today_input_status, list_health_records

def render():
    st.title("管理者ダッシュボード")
    st.caption("DB安定版・健康チェックCRUD対応")

    facility_id = st.session_state.get("facility_id", "default")

    st.subheader("今日の健康チェック入力状況")
    target_date = st.date_input("確認日", value=dt.date.today(), key="dash_target_date")
    status = today_input_status(facility_id, target_date)

    if status.empty:
        st.info("利用者がまだ登録されていません。左メニューの「利用者登録」から登録してください。")
    else:
        total = len(status)
        done = int(status["done"].sum())
        st.metric("入力済み / 登録利用者", f"{done} / {total}")
        st.dataframe(status[["user_name", "入力状況"]], use_container_width=True)

    st.subheader("直近の健康チェック履歴")
    df = list_health_records(facility_id=facility_id, limit=20)
    if df.empty:
        st.info("健康チェック記録はまだありません。")
    else:
        st.dataframe(df, use_container_width=True)
