from __future__ import annotations
import streamlit as st
from datetime import date
from sqlalchemy.exc import IntegrityError
from services.health_service import list_users, add_user, update_user, delete_user

def render():
    st.title("利用者登録")
    st.caption("利用者の登録・更新・無効化を行います。")
    mode = st.radio("操作", ["新規登録", "一覧・更新", "無効化"], horizontal=True)

    if mode == "新規登録":
        with st.form("user_create"):
            c1, c2, c3 = st.columns(3)
            user_code = c1.text_input("利用者コード", placeholder="例：001")
            user_name = c2.text_input("利用者名", placeholder="例：さくら")
            room = c3.text_input("居室", placeholder="例：101")
            c4, c5 = st.columns(2)
            birth_date = c4.date_input("生年月日", value=None)
            gender = c5.selectbox("性別", ["", "女性", "男性", "その他・未設定"])
            memo = st.text_area("メモ")
            if st.form_submit_button("登録する", type="primary"):
                if not user_code or not user_name:
                    st.error("利用者コードと利用者名は必須です。")
                else:
                    try:
                        add_user(user_code, user_name, room, birth_date, gender, memo)
                        st.success("利用者を登録しました。")
                        st.rerun()
                    except IntegrityError:
                        st.error("同じ利用者コードがすでに登録されています。")

    elif mode == "一覧・更新":
        keyword = st.text_input("検索", placeholder="利用者名・コード・居室")
        df = list_users(active_only=False, keyword=keyword)
        st.dataframe(df, use_container_width=True, hide_index=True)
        if not df.empty:
            opts = {f'ID:{r["id"]}｜{r["user_code"]}｜{r["user_name"]}': int(r["id"]) for _, r in df.iterrows()}
            selected = st.selectbox("更新する利用者", list(opts.keys()))
            row = df[df["id"] == opts[selected]].iloc[0]
            with st.form("user_update"):
                c1, c2, c3 = st.columns(3)
                user_code = c1.text_input("利用者コード", value=str(row.get("user_code") or ""))
                user_name = c2.text_input("利用者名", value=str(row.get("user_name") or ""))
                room = c3.text_input("居室", value=str(row.get("room") or ""))
                c4, c5, c6 = st.columns(3)
                birth_value = row.get("birth_date") if row.get("birth_date") else None
                birth_date = c4.date_input("生年月日", value=birth_value)
                gender = c5.selectbox("性別", ["", "女性", "男性", "その他・未設定"], index=0)
                is_active = c6.checkbox("有効", value=bool(row.get("is_active", True)))
                memo = st.text_area("メモ", value=str(row.get("memo") or ""))
                if st.form_submit_button("更新する", type="primary"):
                    try:
                        update_user(opts[selected], user_code, user_name, room, birth_date, gender, memo, is_active)
                        st.success("利用者情報を更新しました。")
                        st.rerun()
                    except IntegrityError:
                        st.error("同じ利用者コードがすでに登録されています。")
    else:
        df = list_users(active_only=True)
        if df.empty:
            st.info("有効な利用者はいません。")
            return
        opts = {f'ID:{r["id"]}｜{r["user_code"]}｜{r["user_name"]}': int(r["id"]) for _, r in df.iterrows()}
        selected = st.selectbox("無効化する利用者", list(opts.keys()))
        st.warning("履歴保護のため、完全削除ではなく無効化します。")
        if st.button("無効化する"):
            delete_user(opts[selected])
            st.success("利用者を無効化しました。")
            st.rerun()
