import streamlit as st
import pandas as pd
from datetime import date
from services.health_service import today_input_status, list_health_records

def render():
    st.title("管理者ダッシュボード")
    st.caption("DB安定版・健康チェックCRUD対応")

    fid = st.session_state.get("facility_id", "default")

    st.subheader("今日の健康チェック入力状況")
    status = today_input_status(date.today().isoformat(), fid)
    if status:
        st.dataframe(pd.DataFrame(status), use_container_width=True, hide_index=True)
    else:
        st.info("利用者登録がまだありません。メニューの「利用者登録」から登録してください。")

    st.subheader("直近の健康チェック履歴")
    rows = list_health_records(facility_id=fid, limit=20)
    if rows:
        df = pd.DataFrame(rows).rename(columns={
            "id": "ID",
            "record_date": "記録日",
            "user_name": "利用者名",
            "temperature": "体温",
            "bp_high": "血圧上",
            "bp_low": "血圧下",
            "pulse": "脈拍",
            "spo2": "SpO2",
            "weight": "体重",
            "meal_rate": "食事摂取率",
            "memo": "メモ",
        })
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("健康チェック記録はまだありません。")
