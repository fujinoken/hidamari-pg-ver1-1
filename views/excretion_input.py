import datetime as dt
import streamlit as st
from services.health_service import add_excretion_record


def render():
    st.title("排泄チェック入力")
    user = st.session_state.get("user", {})
    with st.form("excretion_form"):
        record_date = st.date_input("記録日", value=dt.date.today())
        user_name = st.text_input("利用者名")
        urination = st.number_input("排尿回数", 0, 20, 0, 1)
        defecation = st.number_input("排便回数", 0, 20, 0, 1)
        memo = st.text_area("メモ")
        submitted = st.form_submit_button("登録")
    if submitted:
        if not user_name.strip():
            st.error("利用者名を入力してください。")
            return
        add_excretion_record({
            "facility_id": user.get("facility_id", "default"),
            "user_id": user_name.strip(),
            "user_name": user_name.strip(),
            "record_date": str(record_date),
            "urination": urination,
            "defecation": defecation,
            "memo": memo,
            "created_by": user.get("name", ""),
        })
        st.success("排泄チェックを登録しました。")
