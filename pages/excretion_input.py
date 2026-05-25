from __future__ import annotations
import datetime as dt
import streamlit as st
from services.health_service import list_residents, upsert_excretion_record

def render(user: dict):
    st.title("排泄チェック入力")
    facility_id = user.get("facility_id", "default")
    residents = list_residents(facility_id)
    if not residents:
        st.warning("利用者が登録されていません。")
        return

    name_to_id = {r["name"]: r["id"] for r in residents}
    with st.form("excretion_form"):
        record_date = st.date_input("記録日", value=dt.date.today())
        resident_name = st.selectbox("利用者", list(name_to_id.keys()))
        urination_count = st.number_input("排尿回数", min_value=0, max_value=30, value=0, step=1)
        defecation_count = st.number_input("排便回数", min_value=0, max_value=20, value=0, step=1)
        stool_condition = st.selectbox("便の状態", ["", "普通", "軟便", "硬便", "下痢", "少量"])
        memo = st.text_area("メモ")
        submitted = st.form_submit_button("登録・更新")

    if submitted:
        upsert_excretion_record({
            "facility_id": facility_id,
            "resident_id": name_to_id[resident_name],
            "record_date": record_date,
            "urination_count": urination_count,
            "defecation_count": defecation_count,
            "stool_condition": stool_condition,
            "memo": memo,
            "staff_id": user.get("id"),
        })
        st.success("排泄チェックを登録・更新しました。")
