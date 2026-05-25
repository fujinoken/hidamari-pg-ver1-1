
from __future__ import annotations
import streamlit as st
from services.users_service import list_users, add_user, update_user
from services.export_service import export_table_df, df_to_csv_bytes, csv_filename
from services.backup_service import create_logical_backup_summary
from db.connection import get_engine
from db.schema import audit_logs
from config.settings import DEFAULT_FACILITY_ID
from sqlalchemy import select

def render(current_user: dict):
    st.header("管理者画面")
    tabs = st.tabs(["利用者マスタ", "監査ログ", "CSV出力", "バックアップ"])

    with tabs[0]:
        st.subheader("利用者マスタ")
        df = list_users(active_only=False)
        st.dataframe(df, use_container_width=True, hide_index=True)
        with st.form("add_user_form"):
            name = st.text_input("新規利用者名")
            memo = st.text_area("メモ")
            if st.form_submit_button("利用者を追加", type="primary", use_container_width=True):
                add_user(name, memo)
                st.success("追加しました。")
                st.rerun()

    with tabs[1]:
        st.subheader("監査ログ")
        with get_engine().begin() as conn:
            rows = conn.execute(select(audit_logs).where(audit_logs.c.facility_id == DEFAULT_FACILITY_ID).order_by(audit_logs.c.created_at.desc()).limit(500)).mappings().all()
        import pandas as pd
        adf = pd.DataFrame([dict(r) for r in rows])
        st.dataframe(adf, use_container_width=True, hide_index=True)

    with tabs[2]:
        st.subheader("CSV出力")
        table = st.selectbox("出力対象", ["health_records", "excretion_records", "handover_logs", "users", "audit_logs"])
        df = export_table_df(table)
        st.dataframe(df.head(100), use_container_width=True, hide_index=True)
        st.download_button(
            "CSVをダウンロード",
            data=df_to_csv_bytes(df),
            file_name=csv_filename(table),
            mime="text/csv",
            use_container_width=True,
        )

    with tabs[3]:
        st.subheader("バックアップ")
        st.caption("PostgreSQL版では、DB全体の物理バックアップはNeon側で管理し、この画面では論理バックアップ記録を残します。")
        if st.button("論理バックアップ記録を作成", type="primary", use_container_width=True):
            result = create_logical_backup_summary(current_user)
            st.success("バックアップ記録を作成しました。")
            st.json(result)
