import datetime as dt
import streamlit as st
from services.health_service import add_health_record


def render():
    st.title("健康チェック入力")
    user = st.session_state.get("user", {})
    with st.form("health_form"):
        record_date = st.date_input("記録日", value=dt.date.today())
        user_name = st.text_input("利用者名")
        temperature = st.number_input("体温", 30.0, 45.0, 36.5, 0.1)
        bp_h = st.number_input("血圧 上", 0.0, 250.0, 120.0, 1.0)
        bp_l = st.number_input("血圧 下", 0.0, 180.0, 70.0, 1.0)
        pulse = st.number_input("脈拍", 0.0, 220.0, 70.0, 1.0)
        spo2 = st.number_input("SpO2", 0.0, 100.0, 96.0, 1.0)
        weight = st.number_input("体重", 0.0, 200.0, 50.0, 0.1)
        meal_rate = st.number_input("食事摂取率", 0.0, 100.0, 80.0, 5.0)
        memo = st.text_area("メモ")
        submitted = st.form_submit_button("登録")
    if submitted:
        if not user_name.strip():
            st.error("利用者名を入力してください。")
            return
        add_health_record({
            "facility_id": user.get("facility_id", "default"),
            "user_id": user_name.strip(),
            "user_name": user_name.strip(),
            "record_date": str(record_date),
            "temperature": temperature,
            "blood_pressure_high": bp_h,
            "blood_pressure_low": bp_l,
            "pulse": pulse,
            "spo2": spo2,
            "weight": weight,
            "meal_rate": meal_rate,
            "memo": memo,
            "created_by": user.get("name", ""),
        })
        st.success("健康チェックを登録しました。")
