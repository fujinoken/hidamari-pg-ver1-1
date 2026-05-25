from __future__ import annotations

import streamlit as st
import pandas as pd
from services.users_service import list_user_options
from services.health_service import upsert_health_record, list_health_records, latest_weight_by_user
from services.audit_service import add_audit_log
from utils.time_utils import today_jst
from utils.text_utils import safe_float, safe_int
from components.ui import header


def render(current_user: dict):
    header("健康チェック入力", "体重は任意です。未測定の日は空欄のままで大丈夫です。")
    options = list_user_options()
    if not options:
        st.warning("利用者マスタを先に登録してください。")
        return

    user_labels = {name: uid for uid, name in options}
    with st.form("health_form"):
        record_date = st.date_input("記録日", value=today_jst())
        user_name = st.selectbox("利用者", list(user_labels.keys()))
        user_id = user_labels[user_name]
        latest_weight = latest_weight_by_user(user_id)
        if latest_weight:
            st.caption(f"最新体重：{latest_weight.weight}kg（{latest_weight.record_date} 測定）")
        else:
            st.caption("最新体重：未測定")

        c1, c2, c3, c4 = st.columns(4)
        temperature = c1.number_input("体温", min_value=30.0, max_value=45.0, value=36.5, step=0.1)
        bp_high = c2.number_input("血圧上", min_value=0, max_value=250, value=120, step=1)
        bp_low = c3.number_input("血圧下", min_value=0, max_value=180, value=70, step=1)
        pulse = c4.number_input("脈拍", min_value=0, max_value=220, value=70, step=1)

        c5, c6, c7 = st.columns(3)
        spo2 = c5.number_input("SpO2", min_value=0, max_value=100, value=96, step=1)
        weight_raw = c6.text_input("体重（任意）", placeholder="未測定なら空欄")
        water_ml = c7.number_input("水分摂取量ml（任意）", min_value=0, max_value=5000, value=0, step=50)

        c8, c9, c10 = st.columns(3)
        breakfast = c8.slider("朝食摂取率", 0, 100, 80, 10)
        lunch = c9.slider("昼食摂取率", 0, 100, 80, 10)
        dinner = c10.slider("夕食摂取率", 0, 100, 80, 10)

        family_note = st.text_area("家族共有メモ", placeholder="共有したいことを短く記録")
        change_note = st.text_area("気になる変化", placeholder="事実・気づき・次に見ることを責めずに記録")
        submitted = st.form_submit_button("健康チェックを保存", type="primary", use_container_width=True)

    if submitted:
        data = {
            "record_date": record_date,
            "user_id": user_id,
            "temperature": float(temperature),
            "bp_high": int(bp_high),
            "bp_low": int(bp_low),
            "pulse": int(pulse),
            "spo2": int(spo2),
            "weight": safe_float(weight_raw, None),
            "breakfast_rate": int(breakfast),
            "lunch_rate": int(lunch),
            "dinner_rate": int(dinner),
            "water_ml": safe_int(water_ml, None),
            "family_note": family_note,
            "change_note": change_note,
            "input_by": current_user.get("display_name", ""),
        }
        upsert_health_record(data)
        add_audit_log(current_user.get("login_id"), current_user.get("role"), "健康チェック保存", "health_records", summary=f"{record_date} {user_name}")
        st.success("保存しました。")
        st.rerun()

    st.subheader("最近の健康記録")
    rows = list_health_records(limit=200)
    if rows:
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
