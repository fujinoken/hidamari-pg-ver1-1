from __future__ import annotations

import streamlit as st
import pandas as pd
from services.users_service import list_users, create_user, update_user
from services.audit_service import list_audit_logs, add_audit_log
from services.backup_service import create_export_zip
from components.ui import header


def render(current_user: dict):
    if current_user.get("role") != "admin":
        st.warning("管理者専用画面です。")
        return

    header("管理者画面", "利用者マスタ・監査ログ・バックアップ方針を管理します。")
    tab1, tab2, tab3 = st.tabs(["利用者マスタ", "監査ログ", "バックアップ"])

    with tab1:
        st.subheader("利用者登録")
        with st.form("user_create"):
            display_name = st.text_input("利用者名")
            basic_info = st.text_area("基本情報")
            living_status = st.text_area("生活状況")
            notes = st.text_area("備考")
            submitted = st.form_submit_button("利用者を登録", type="primary", use_container_width=True)
        if submitted:
            if not display_name.strip():
                st.error("利用者名を入力してください。")
            else:
                user = create_user(display_name, basic_info, living_status, notes)
                add_audit_log(current_user.get("login_id"), current_user.get("role"), "利用者登録", "users", user.id, display_name)
                st.success("登録しました。")
                st.rerun()

        users = list_users(include_hidden=True)
        if users:
            rows = [{"ID": u.id, "user_code": u.user_code, "利用者名": u.display_name, "表示": u.is_visible, "基本情報": u.basic_info, "生活状況": u.living_status, "備考": u.notes} for u in users]
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    with tab2:
        st.subheader("監査ログ")
        logs = list_audit_logs(500)
        if logs:
            st.dataframe(pd.DataFrame(logs), use_container_width=True, hide_index=True)
        else:
            st.caption("監査ログはまだありません。")

    with tab3:
        st.subheader("バックアップ方針")
        st.info("PostgreSQL版では、DBファイル丸ごとではなく、主要テーブルの論理バックアップCSV ZIPを作成します。")
        if st.button("論理バックアップZIPを作成", type="primary", use_container_width=True):
            data = create_export_zip()
            add_audit_log(current_user.get("login_id"), current_user.get("role"), "バックアップ作成", "backup", summary="PostgreSQL論理CSVバックアップ")
            st.download_button("バックアップZIPをダウンロード", data=data, file_name="hidamari_pg_backup.zip", mime="application/zip", use_container_width=True)
