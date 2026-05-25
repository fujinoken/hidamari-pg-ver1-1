from datetime import date
import streamlit as st
from services.health_service import list_residents, add_health_record


def render():
    st.title("健康チェック入力")
    residents = list_residents()
    names = [r["name"] for r in residents]
    name_to_id = {r["name"]: r["id"] for r in residents}

    with st.form("health_form"):
        record_date = st.date_input("確認日", value=date.today())
        resident_name = st.selectbox("利用者", names)
        temperature = st.number_input("体温", min_value=30.0, max_value=45.0, value=36.5, step=0.1)
        bp_high = st.number_input("血圧 上", min_value=0, max_value=250, value=120, step=1)
        bp_low = st.number_input("血圧 下", min_value=0, max_value=200, value=70, step=1)
        pulse = st.number_input("脈拍", min_value=0, max_value=220, value=70, step=1)
        spo2 = st.number_input("SpO2", min_value=0.0, max_value=100.0, value=96.0, step=1.0)
        weight = st.number_input("体重", min_value=0.0, max_value=200.0, value=50.0, step=0.1)
        meal_rate = st.number_input("食事摂取率（%）", min_value=0.0, max_value=100.0, value=100.0, step=10.0)
        memo = st.text_area("メモ")
        staff_name = st.text_input("職員名", value=st.session_state.get("user_name", ""))
        submitted = st.form_submit_button("登録")

    if submitted:
        add_health_record({
            "record_date": record_date,
            "resident_id": name_to_id[resident_name],
            "resident_name": resident_name,
            "temperature": temperature,
            "blood_pressure_high": int(bp_high),
            "blood_pressure_low": int(bp_low),
            "pulse": int(pulse),
            "spo2": spo2,
            "weight": weight,
            "meal_rate": meal_rate,
            "memo": memo,
            "staff_name": staff_name,
        })
        st.success("健康チェックを登録しました。")
