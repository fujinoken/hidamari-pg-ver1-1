from datetime import date
import streamlit as st
from services.health_service import list_residents, add_excretion_record


def render():
    st.title("排泄チェック入力")
    residents = list_residents()
    names = [r["name"] for r in residents]
    name_to_id = {r["name"]: r["id"] for r in residents}

    with st.form("excretion_form"):
        record_date = st.date_input("確認日", value=date.today())
        resident_name = st.selectbox("利用者", names)
        urination = st.selectbox("排尿", ["あり", "なし", "少量", "多量"])
        bowel_movement = st.selectbox("排便", ["なし", "あり", "少量", "普通", "多量"])
        memo = st.text_area("メモ")
        staff_name = st.text_input("職員名", value=st.session_state.get("user_name", ""))
        submitted = st.form_submit_button("登録")

    if submitted:
        add_excretion_record({
            "record_date": record_date,
            "resident_id": name_to_id[resident_name],
            "resident_name": resident_name,
            "urination": urination,
            "bowel_movement": bowel_movement,
            "memo": memo,
            "staff_name": staff_name,
        })
        st.success("排泄チェックを登録しました。")
