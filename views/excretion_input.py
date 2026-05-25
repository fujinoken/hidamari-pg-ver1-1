import streamlit as st
from datetime import date

def render():
    st.title("排泄チェック入力")
    st.info("この版では健康チェックCRUDを優先しています。排泄チェックは次版で拡張します。")
    st.date_input("記録日", value=date.today())
