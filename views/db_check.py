import streamlit as st
import pandas as pd
from db.migrations import schema_report

def render():
    st.title("DB確認")
    st.caption("エラー予防用。各テーブルの列構成を確認できます。")
    report = schema_report()
    for table, cols in report.items():
        st.subheader(table)
        df = pd.DataFrame([{"列名": k, "型": v} for k, v in cols.items()])
        st.dataframe(df, use_container_width=True, hide_index=True)
