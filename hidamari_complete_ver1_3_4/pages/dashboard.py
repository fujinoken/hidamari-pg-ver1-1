import streamlit as st
import pandas as pd
from db.migrations import init_db
from services.health_service import list_health_records, list_excretion_records

init_db()
st.title("ダッシュボード")
if not st.session_state.get("logged_in"):
    st.warning("先に app ページでログインしてください。")
    st.stop()

st.subheader("健康チェック 最新データ")
st.dataframe(pd.DataFrame(list_health_records()), use_container_width=True)

st.subheader("排泄チェック 最新データ")
st.dataframe(pd.DataFrame(list_excretion_records()), use_container_width=True)
