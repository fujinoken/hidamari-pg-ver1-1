import streamlit as st
from datetime import date
from db.migrations import init_db
from services.auth_service import list_users
from services.health_service import upsert_health_record
from config.settings import DEFAULT_FACILITY_ID

init_db()
st.title("健康チェック入力")
if not st.session_state.get("logged_in"):
    st.warning("先に app ページでログインしてください。")
    st.stop()

users = list_users(DEFAULT_FACILITY_ID)
user_map = {u["display_name"]: u["id"] for u in users}
if not user_map:
    st.error("利用者がありません。")
    st.stop()

with st.form("health_form"):
    target = st.selectbox("利用者", list(user_map.keys()))
    record_date = st.date_input("日付", value=date.today())
    temperature = st.number_input("体温", min_value=30.0, max_value=45.0, value=36.5, step=0.1)
    bp_high = st.number_input("血圧 上", min_value=0, max_value=300, value=120, step=1)
    bp_low = st.number_input("血圧 下", min_value=0, max_value=200, value=80, step=1)
    pulse = st.number_input("脈拍", min_value=0, max_value=250, value=70, step=1)
    spo2 = st.number_input("SpO2", min_value=0.0, max_value=100.0, value=96.0, step=1.0)
    weight = st.number_input("体重", min_value=0.0, max_value=200.0, value=50.0, step=0.1)
    meal_rate = st.number_input("食事摂取率", min_value=0.0, max_value=100.0, value=100.0, step=5.0)
    memo = st.text_area("メモ")
    submitted = st.form_submit_button("登録・更新")

if submitted:
    upsert_health_record({
        "facility_id": DEFAULT_FACILITY_ID,
        "user_id": user_map[target],
        "record_date": str(record_date),
        "temperature": temperature,
        "blood_pressure_high": bp_high,
        "blood_pressure_low": bp_low,
        "pulse": pulse,
        "spo2": spo2,
        "weight": weight,
        "meal_rate": meal_rate,
        "memo": memo,
        "created_by": st.session_state.user["id"],
    })
    st.success("登録・更新しました。")
