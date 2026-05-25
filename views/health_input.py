import datetime as dt
import streamlit as st
import pandas as pd
from services.health_service import (
    create_user, list_users, get_user_options,
    save_health_record, update_health_record, delete_health_record,
    list_health_records, today_input_status
)

def _fmt_date(v):
    try:
        return pd.to_datetime(v).date()
    except Exception:
        return dt.date.today()

def render():
    st.title("健康チェック入力")
    st.caption("利用者登録・保存・更新・削除・一覧検索・今日の入力状況")

    facility_id = st.session_state.get("facility_id", "default")

    tab_user, tab_new, tab_status, tab_search, tab_edit = st.tabs(
        ["利用者登録", "新規入力", "今日の入力状況", "一覧検索", "更新・削除"]
    )

    with tab_user:
        st.subheader("利用者登録")
        with st.form("user_form", clear_on_submit=True):
            user_code = st.text_input("利用者コード（任意）")
            user_name = st.text_input("利用者名")
            submitted = st.form_submit_button("利用者を登録")
            if submitted:
                try:
                    create_user(user_name=user_name, user_code=user_code, facility_id=facility_id)
                    st.success("利用者を登録しました。")
                    st.rerun()
                except Exception as e:
                    st.error(f"登録できませんでした: {e}")

        st.subheader("登録済み利用者")
        users = list_users(facility_id)
        if users:
            st.dataframe(pd.DataFrame(users)[["user_code", "user_name", "is_active"]], use_container_width=True)
        else:
            st.info("利用者はまだ登録されていません。")

    with tab_new:
        st.subheader("健康チェックを保存")
        options = get_user_options(facility_id)
        if not options:
            st.warning("先に利用者を登録してください。")
        else:
            with st.form("health_new_form", clear_on_submit=True):
                record_date = st.date_input("記録日", value=dt.date.today())
                selected = st.selectbox("利用者名", list(options.keys()))
                col1, col2, col3 = st.columns(3)
                with col1:
                    temperature = st.number_input("体温", min_value=30.0, max_value=45.0, value=36.5, step=0.1)
                    bp_high = st.number_input("血圧 上", min_value=0.0, max_value=250.0, value=120.0, step=1.0)
                    bp_low = st.number_input("血圧 下", min_value=0.0, max_value=180.0, value=70.0, step=1.0)
                with col2:
                    pulse = st.number_input("脈拍", min_value=0.0, max_value=220.0, value=70.0, step=1.0)
                    spo2 = st.number_input("SpO2", min_value=0.0, max_value=100.0, value=96.0, step=1.0)
                    weight = st.number_input("体重", min_value=0.0, max_value=200.0, value=50.0, step=0.1)
                with col3:
                    meal_rate = st.number_input("食事摂取率", min_value=0.0, max_value=100.0, value=80.0, step=5.0)
                memo = st.text_area("メモ")
                submitted = st.form_submit_button("保存")
                if submitted:
                    try:
                        save_health_record(
                            record_date=record_date,
                            user_id=options[selected],
                            temperature=temperature,
                            bp_high=bp_high,
                            bp_low=bp_low,
                            pulse=pulse,
                            spo2=spo2,
                            weight=weight,
                            meal_rate=meal_rate,
                            memo=memo,
                            facility_id=facility_id,
                        )
                        st.success("健康チェックを保存しました。")
                        st.rerun()
                    except Exception as e:
                        st.error(f"保存できませんでした: {e}")

    with tab_status:
        st.subheader("今日の入力状況")
        target_date = st.date_input("確認日", value=dt.date.today(), key="health_status_date")
        df = today_input_status(facility_id, target_date)
        if df.empty:
            st.info("利用者が登録されていません。")
        else:
            st.dataframe(df[["user_name", "入力状況"]], use_container_width=True)

    with tab_search:
        st.subheader("一覧検索")
        options = get_user_options(facility_id)
        col1, col2, col3 = st.columns(3)
        with col1:
            start_date = st.date_input("開始日", value=dt.date.today().replace(day=1), key="search_start")
        with col2:
            end_date = st.date_input("終了日", value=dt.date.today(), key="search_end")
        with col3:
            user_label = st.selectbox("利用者", ["全員"] + list(options.keys()), key="search_user")
        user_id = None if user_label == "全員" else options.get(user_label)
        df = list_health_records(facility_id, start_date, end_date, user_id)
        if df.empty:
            st.info("該当する記録はありません。")
        else:
            st.dataframe(df, use_container_width=True)

    with tab_edit:
        st.subheader("更新・削除")
        df = list_health_records(facility_id, limit=200)
        if df.empty:
            st.info("更新・削除できる記録はまだありません。")
        else:
            df = df.copy()
            df["表示"] = df.apply(lambda r: f"{r['record_date']}｜{r['user_name']}｜体温:{r.get('temperature','')}", axis=1)
            selected_label = st.selectbox("編集する記録を選択", df["表示"].tolist())
            row = df[df["表示"] == selected_label].iloc[0].to_dict()

            options = get_user_options(facility_id)
            reverse = {v: k for k, v in options.items()}
            current_user_label = reverse.get(str(row["user_id"]), list(options.keys())[0] if options else "")

            with st.form("edit_form"):
                record_date = st.date_input("記録日", value=_fmt_date(row["record_date"]), key="edit_date")
                selected_user = st.selectbox(
                    "利用者名",
                    list(options.keys()),
                    index=list(options.keys()).index(current_user_label) if current_user_label in options else 0,
                    key="edit_user"
                )
                col1, col2, col3 = st.columns(3)
                with col1:
                    temperature = st.number_input("体温", value=float(row["temperature"] or 0), step=0.1, key="edit_temp")
                    bp_high = st.number_input("血圧 上", value=float(row["bp_high"] or 0), step=1.0, key="edit_bph")
                    bp_low = st.number_input("血圧 下", value=float(row["bp_low"] or 0), step=1.0, key="edit_bpl")
                with col2:
                    pulse = st.number_input("脈拍", value=float(row["pulse"] or 0), step=1.0, key="edit_pulse")
                    spo2 = st.number_input("SpO2", value=float(row["spo2"] or 0), step=1.0, key="edit_spo2")
                    weight = st.number_input("体重", value=float(row["weight"] or 0), step=0.1, key="edit_weight")
                with col3:
                    meal_rate = st.number_input("食事摂取率", value=float(row["meal_rate"] or 0), step=5.0, key="edit_meal")
                memo = st.text_area("メモ", value=str(row.get("memo") or ""), key="edit_memo")

                col_update, col_delete = st.columns(2)
                update_btn = col_update.form_submit_button("更新")
                delete_btn = col_delete.form_submit_button("削除")

                if update_btn:
                    try:
                        update_health_record(
                            row["id"],
                            record_date=record_date,
                            user_id=options[selected_user],
                            temperature=temperature,
                            bp_high=bp_high,
                            bp_low=bp_low,
                            pulse=pulse,
                            spo2=spo2,
                            weight=weight,
                            meal_rate=meal_rate,
                            memo=memo,
                        )
                        st.success("更新しました。")
                        st.rerun()
                    except Exception as e:
                        st.error(f"更新できませんでした: {e}")

                if delete_btn:
                    try:
                        delete_health_record(row["id"])
                        st.success("削除しました。")
                        st.rerun()
                    except Exception as e:
                        st.error(f"削除できませんでした: {e}")
