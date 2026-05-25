import streamlit as st
import pandas as pd
from datetime import date
from services.health_service import today_input_status, list_health_records

def render():
    facility_id = st.session_state["facility_id"]
    st.title("管理者ダッシュボード")
    st.caption("DB安定版・健康チェックCRUD対応")

    st.subheader("今日の健康チェック入力状況")
    target_date = st.date_input("確認日", value=date.today(), key="dash_date").isoformat()
    rows = today_input_status(facility_id, target_date)
    if rows:
        df = pd.DataFrame(rows)
        st.dataframe(df[["user_name", "room", "status"]], use_container_width=True, hide_index=True)
        done = (df["status"] == "入力済み").sum()
        st.info(f"入力済み：{done}名 / 対象：{len(df)}名")
    else:
        st.warning("利用者が登録されていません。まず「利用者登録」から登録してください。")

    st.subheader("直近の健康チェック履歴")
    records = list_health_records(facility_id, limit=20)
    if records:
        st.dataframe(pd.DataFrame(records), use_container_width=True, hide_index=True)
    else:
        st.info("健康チェック記録はまだありません。")
