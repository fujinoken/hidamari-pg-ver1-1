import streamlit as st
from datetime import date

def render():
    st.title("申し送り")
    st.info("この版では健康チェックCRUDを優先しています。申し送りは次版で拡張します。")
    st.date_input("記録日", value=date.today())
