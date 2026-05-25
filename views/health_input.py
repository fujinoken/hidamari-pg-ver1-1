from __future__ import annotations
from datetime import date, timedelta
import streamlit as st
import pandas as pd
from services.health_service import list_users, add_user, list_health_records, upsert_health_record, update_health_record, delete_health_record, get_health_record, today_input_status
from sqlalchemy.exc import IntegrityError

def _user_options():
    users_df = list_users(active_only=True)
    if users_df.empty:
        return users_df, {}
    return users_df, {f'{r["user_code"]}｜{r["user_name"]}｜{r.get("room") or ""}': int(r["id"]) for _, r in users_df.iterrows()}

def _health_form(prefix: str, default: dict | None = None):
    default = default or {}
    c1, c2, c3 = st.columns(3)
    temperature = c1.number_input("体温", min_value=30.0, max_value=45.0, value=float(default.get("temperature") or 36.5), step=0.1, format="%.1f", key=f"{prefix}_temp")
    bp_high = c2.number_input("血圧 上", min_value=50, max_value=250, value=int(default.get("blood_pressure_high") or 120), step=1, key=f"{prefix}_bph")
    bp_low = c3.number_input("血圧 下", min_value=30, max_value=150, value=int(default.get("blood_pressure_low") or 70), step=1, key=f"{prefix}_bpl")
    c4, c5, c6 = st.columns(3)
    pulse = c4.number_input("脈拍", min_value=30, max_value=200, value=int(default.get("pulse") or 70), step=1, key=f"{prefix}_pulse")
    spo2 = c5.number_input("SpO2", min_value=50, max_value=100, value=int(default.get("spo2") or 96), step=1, key=f"{prefix}_spo2")
    weight = c6.number_input("体重", min_value=0.0, max_value=200.0, value=float(default.get("weight") or 50.0), step=0.1, format="%.1f", key=f"{prefix}_weight")
    c7, c8 = st.columns(2)
    meal_rate = c7.slider("食事摂取率（%）", 0, 100, int(default.get("meal_rate") or 100), 10, key=f"{prefix}_meal")
    water_amount = c8.number_input("水分量（ml）", min_value=0, max_value=5000, value=int(default.get("water_amount") or 0), step=50, key=f"{prefix}_water")
    family_memo = st.text_area("家族共有メモ", value=default.get("family_memo") or "", key=f"{prefix}_family")
    staff_memo = st.text_area("職員メモ", value=default.get("staff_memo") or "", key=f"{prefix}_staffmemo")
    staff_name = st.text_input("記入者名", value=default.get("staff_name") or st.session_state.get("staff_name", ""), key=f"{prefix}_staff")
    return dict(temperature=float(temperature), blood_pressure_high=int(bp_high), blood_pressure_low=int(bp_low), pulse=int(pulse), spo2=int(spo2), weight=float(weight), meal_rate=int(meal_rate), water_amount=int(water_amount), family_memo=family_memo, staff_memo=staff_memo, staff_name=staff_name)

def render():
    st.title("健康チェック入力")
    st.caption("利用者登録／保存／更新／削除／一覧検索／今日の入力状況をこの画面で操作できます。")

    mode = st.radio(
        "操作を選択",
        ["今日の入力状況", "利用者登録", "健康チェック保存", "一覧検索", "更新", "削除"],
        horizontal=True,
    )

    if mode == "今日の入力状況":
        st.subheader("今日の入力状況")
        target_date = st.date_input("確認日", value=date.today(), key="status_date")
        df = today_input_status(target_date)
        if df.empty:
            st.info("利用者が登録されていません。")
        else:
            done = (df["入力状況"] == "入力済み").sum()
            total = len(df)
            st.metric("入力済み", f"{done}/{total} 名")
            st.dataframe(df, use_container_width=True, hide_index=True)
        return

    if mode == "利用者登録":
        st.subheader("利用者登録")
        with st.form("quick_user_create"):
            c1, c2, c3 = st.columns(3)
            user_code = c1.text_input("利用者コード", placeholder="例：001")
            user_name = c2.text_input("利用者名", placeholder="例：さくら")
            room = c3.text_input("居室", placeholder="例：101")
            c4, c5 = st.columns(2)
            birth_date = c4.date_input("生年月日", value=None)
            gender = c5.selectbox("性別", ["", "女性", "男性", "その他・未設定"])
            memo = st.text_area("メモ")
            if st.form_submit_button("利用者を登録する", type="primary"):
                if not user_code or not user_name:
                    st.error("利用者コードと利用者名は必須です。")
                else:
                    try:
                        add_user(user_code, user_name, room, birth_date, gender, memo)
                        st.success("利用者を登録しました。")
                        st.rerun()
                    except IntegrityError:
                        st.error("同じ利用者コードがすでに登録されています。")
        st.divider()
        st.subheader("登録済み利用者")
        st.dataframe(list_users(active_only=True), use_container_width=True, hide_index=True)
        return

    users_df, user_options = _user_options()
    if users_df.empty:
        st.warning("利用者が登録されていません。先に『利用者登録』を行ってください。")
        return

    if mode == "健康チェック保存":
        st.subheader("健康チェック保存")
        target_date = st.date_input("記録日", value=date.today(), key="create_date")
        selected_user = st.selectbox("利用者", list(user_options.keys()), key="create_user")
        with st.form("health_create_form"):
            values = _health_form("create")
            if st.form_submit_button("保存する", type="primary"):
                result = upsert_health_record(target_date, user_options[selected_user], **values)
                st.success("健康チェックを保存しました。" if result == "created" else "同じ日付・同じ利用者の記録を更新しました。")
                st.rerun()
        return

    if mode == "一覧検索":
        st.subheader("一覧検索")
        c1, c2, c3 = st.columns(3)
        start_date = c1.date_input("開始日", value=date.today() - timedelta(days=7), key="search_start")
        end_date = c2.date_input("終了日", value=date.today(), key="search_end")
        keyword = c3.text_input("キーワード", placeholder="利用者名・コード・居室")
        df = list_health_records(start_date=start_date, end_date=end_date, keyword=keyword)
        if df.empty:
            st.info("該当する記録はありません。")
        else:
            show_cols = ["id", "record_date", "user_code", "user_name", "room", "temperature", "blood_pressure_high", "blood_pressure_low", "pulse", "spo2", "weight", "meal_rate", "water_amount", "family_memo", "staff_memo", "staff_name"]
            st.dataframe(df[show_cols], use_container_width=True, hide_index=True)
            st.download_button("CSVダウンロード", df[show_cols].to_csv(index=False).encode("utf-8-sig"), "health_records.csv", "text/csv")
        return

    recent_df = list_health_records(start_date=date.today() - timedelta(days=90), end_date=date.today())
    if recent_df.empty:
        st.info("対象となる健康チェック記録がありません。")
        return
    options = {f'ID:{r["id"]}｜{r["record_date"]}｜{r["user_name"]}｜{r.get("room") or ""}': int(r["id"]) for _, r in recent_df.iterrows()}

    if mode == "更新":
        st.subheader("健康チェック更新")
        selected = st.selectbox("更新する記録", list(options.keys()), key="update_select")
        record = get_health_record(options[selected])
        if not record:
            st.error("記録を取得できませんでした。")
            return
        user_label = next((k for k, v in user_options.items() if v == int(record["user_id"])), list(user_options.keys())[0])
        record_date = st.date_input("記録日", value=pd.to_datetime(record["record_date"]).date(), key="update_date")
        selected_user = st.selectbox("利用者", list(user_options.keys()), index=list(user_options.keys()).index(user_label), key="update_user")
        with st.form("health_update_form"):
            values = _health_form("update", record)
            if st.form_submit_button("更新する", type="primary"):
                update_health_record(options[selected], record_date=record_date, user_id=user_options[selected_user], **values)
                st.success("健康チェック記録を更新しました。")
                st.rerun()
        return

    if mode == "削除":
        st.subheader("健康チェック削除")
        st.warning("削除すると元に戻せません。")
        selected = st.selectbox("削除する記録", list(options.keys()), key="delete_select")
        confirm = st.checkbox("この記録を削除することを確認しました")
        if st.button("削除する", disabled=not confirm, type="primary"):
            delete_health_record(options[selected])
            st.success("健康チェック記録を削除しました。")
            st.rerun()
