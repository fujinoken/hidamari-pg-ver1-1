from __future__ import annotations
import datetime as dt
import streamlit as st
from services.health_service import list_residents, upsert_health_record

def render(user: dict):
    st.title("健康チェック入力")
    facility_id = user.get("facility_id", "default")
    residents = list_residents(facility_id)
    if not residents:
        st.warning("利用者が登録されていません。")
        return

    name_to_id = {r["name"]: r["id"] for r in residents}
    with st.form("health_form"):
        record_date = st.date_input("記録日", value=dt.date.today())
        resident_name = st.selectbox("利用者", list(name_to_id.keys()))
        c1, c2, c3 = st.columns(3)
        with c1:
            temperature = st.number_input("体温", min_value=30.0, max_value=45.0, value=36.5, step=0.1)
            bp_high = st.number_input("血圧 上", min_value=0, max_value=250, value=120, step=1)
            bp_low = st.number_input("血圧 下", min_value=0, max_value=200, value=70, step=1)
        with c2:
            pulse = st.number_input("脈拍", min_value=0, max_value=250, value=70, step=1)
            spo2 = st.number_input("SpO2", min_value=0, max_value=100, value=96, step=1)
            weight = st.number_input("体重", min_value=0.0, max_value=250.0, value=50.0, step=0.1)
        with c3:
            meal_rate = st.number_input("食事摂取率(%)", min_value=0.0, max_value=100.0, value=100.0, step=5.0)
            water_ml = st.number_input("水分量ml", min_value=0, max_value=5000, value=0, step=50)
        memo = st.text_area("メモ")
        submitted = st.form_submit_button("登録・更新")

    if submitted:
        upsert_health_record({
            "facility_id": facility_id,
            "resident_id": name_to_id[resident_name],
            "record_date": record_date,
            "temperature": temperature,
            "blood_pressure_high": bp_high,
            "blood_pressure_low": bp_low,
            "pulse": pulse,
            "spo2": spo2,
            "weight": weight,
            "meal_rate": meal_rate,
            "water_ml": water_ml,
            "memo": memo,
            "staff_id": user.get("id"),
        })
        st.success("健康チェックを登録・更新しました。")
