import streamlit as st
from datetime import date
from services.auth_service import list_users
from services.health_service import upsert_excretion_record
from config.settings import DEFAULT_FACILITY_ID


def render():
    st.header("排泄チェック入力")
    users = list_users(DEFAULT_FACILITY_ID)
    user_map = {u["display_name"]: u["id"] for u in users if u.get("is_active", 1) == 1}

    if not user_map:
        st.error("利用者が登録されていません。")
        return

    with st.form("excretion_form"):
        target = st.selectbox("利用者", list(user_map.keys()))
        record_date = st.date_input("日付", value=date.today())
        c1, c2 = st.columns(2)
        with c1:
            urine_count = st.number_input("排尿回数", min_value=0, max_value=30, value=0, step=1)
            stool_count = st.number_input("排便回数", min_value=0, max_value=20, value=0, step=1)
        with c2:
            stool_status = st.selectbox("便の状態", ["", "普通", "軟便", "硬便", "下痢", "少量"])
        memo = st.text_area("メモ")
        submitted = st.form_submit_button("登録・更新")

    if submitted:
        upsert_excretion_record({
            "facility_id": DEFAULT_FACILITY_ID,
            "user_id": user_map[target],
            "record_date": str(record_date),
            "urine_count": urine_count,
            "stool_count": stool_count,
            "stool_status": stool_status,
            "memo": memo,
            "created_by": st.session_state.user["id"],
        })
        st.success("排泄チェックを登録・更新しました。")
