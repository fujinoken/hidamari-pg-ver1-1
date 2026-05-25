from datetime import date
import streamlit as st
from services.health_service import get_user_options
from services.excretion_service import save_excretion_record, list_excretion_records

def render():
    st.title("排泄チェック入力")
    user_options = get_user_options()
    if not user_options:
        st.warning("先に「利用者登録」から利用者を登録してください。")
        return

    with st.form("excretion_form"):
        record_date = st.date_input("記録日", value=date.today())
        user_label = st.selectbox("利用者名", list(user_options.keys()))
        urination = st.selectbox("排尿", ["あり", "なし", "少量", "多量"])
        defecation = st.selectbox("排便", ["なし", "あり", "少量", "多量", "軟便", "下痢"])
        memo = st.text_area("メモ")
        submitted = st.form_submit_button("登録")
        if submitted:
            save_excretion_record(user_options[user_label], record_date, urination, defecation, memo)
            st.success("排泄チェックを登録しました。")
            st.rerun()

    st.subheader("排泄チェック履歴")
    df = list_excretion_records()
    if df.empty:
        st.info("記録はまだありません。")
    else:
        st.dataframe(df, use_container_width=True, hide_index=True)
