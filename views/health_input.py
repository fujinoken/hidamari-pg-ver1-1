import streamlit as st
import pandas as pd
from datetime import date, timedelta
from services.health_service import (
    list_users, save_health_record, list_health_records,
    update_health_record, delete_health_record, today_input_status
)

def _user_options(users):
    return {u["user_name"]: str(u["id"]) for u in users}

def _to_float(value, default):
    try:
        return float(value) if value is not None else default
    except Exception:
        return default

def render():
    st.title("健康チェック入力")
    fid = st.session_state.get("facility_id", "default")
    users = list_users(fid)

    if not users:
        st.warning("先に「利用者登録」から利用者を登録してください。")
        return

    user_map = _user_options(users)
    tab1, tab2, tab3, tab4 = st.tabs(["新規保存", "一覧検索・今日の状況", "更新", "削除"])

    with tab1:
        with st.form("health_create"):
            record_date = st.date_input("記録日", value=date.today())
            user_name = st.selectbox("利用者名", list(user_map.keys()))
            temperature = st.number_input("体温", min_value=30.0, max_value=45.0, value=36.5, step=0.1)
            bp_high = st.number_input("血圧 上", min_value=0.0, max_value=300.0, value=120.0, step=1.0)
            bp_low = st.number_input("血圧 下", min_value=0.0, max_value=200.0, value=70.0, step=1.0)
            pulse = st.number_input("脈拍", min_value=0.0, max_value=250.0, value=70.0, step=1.0)
            spo2 = st.number_input("SpO2", min_value=0.0, max_value=100.0, value=96.0, step=1.0)
            weight = st.number_input("体重", min_value=0.0, max_value=250.0, value=50.0, step=0.1)
            meal_rate = st.number_input("食事摂取率", min_value=0.0, max_value=100.0, value=80.0, step=5.0)
            memo = st.text_area("メモ")
            submitted = st.form_submit_button("登録")
            if submitted:
                save_health_record({
                    "user_id": user_map[user_name],
                    "record_date": record_date.isoformat(),
                    "temperature": temperature,
                    "bp_high": bp_high,
                    "bp_low": bp_low,
                    "pulse": pulse,
                    "spo2": spo2,
                    "weight": weight,
                    "meal_rate": meal_rate,
                    "memo": memo,
                }, fid)
                st.success("健康チェックを保存しました。")
                st.rerun()

    with tab2:
        st.subheader("一覧検索")
        c1, c2, c3 = st.columns(3)
        with c1:
            target_user = st.selectbox("利用者", ["全員"] + list(user_map.keys()), key="search_user")
        with c2:
            start_date = st.date_input("開始日", value=date.today() - timedelta(days=30), key="search_start")
        with c3:
            end_date = st.date_input("終了日", value=date.today(), key="search_end")
        keyword = st.text_input("メモ検索（任意）")
        user_id = None if target_user == "全員" else user_map[target_user]
        rows = list_health_records(fid, user_id=user_id, start_date=start_date.isoformat(), end_date=end_date.isoformat(), keyword=keyword)
        if rows:
            df = pd.DataFrame(rows).rename(columns={
                "id": "ID", "record_date": "記録日", "user_name": "利用者名",
                "temperature": "体温", "bp_high": "血圧上", "bp_low": "血圧下",
                "pulse": "脈拍", "spo2": "SpO2", "weight": "体重",
                "meal_rate": "食事摂取率", "memo": "メモ"
            })
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("該当する記録はありません。")

        st.subheader("今日の入力状況")
        status = today_input_status(date.today().isoformat(), fid)
        st.dataframe(pd.DataFrame(status), use_container_width=True, hide_index=True)

    with tab3:
        st.subheader("更新")
        rows = list_health_records(fid, limit=200)
        if not rows:
            st.info("更新できる記録がありません。")
        else:
            labels = [f'{r["id"]}｜{r["record_date"]}｜{r["user_name"]}' for r in rows]
            selected = st.selectbox("更新する記録", labels)
            record_id = int(selected.split("｜")[0])
            current = next(r for r in rows if int(r["id"]) == record_id)
            user_values = list(user_map.values())
            current_user_index = user_values.index(str(current["user_id"])) if str(current["user_id"]) in user_values else 0

            with st.form("health_update"):
                user_name = st.selectbox("利用者名", list(user_map.keys()), index=current_user_index, key="update_user")
                record_date = st.date_input("記録日", value=date.fromisoformat(str(current["record_date"])))
                temperature = st.number_input("体温", value=_to_float(current["temperature"], 36.5), step=0.1, key="update_temp")
                bp_high = st.number_input("血圧 上", value=_to_float(current["bp_high"], 120), step=1.0, key="update_bph")
                bp_low = st.number_input("血圧 下", value=_to_float(current["bp_low"], 70), step=1.0, key="update_bpl")
                pulse = st.number_input("脈拍", value=_to_float(current["pulse"], 70), step=1.0, key="update_pulse")
                spo2 = st.number_input("SpO2", value=_to_float(current["spo2"], 96), step=1.0, key="update_spo2")
                weight = st.number_input("体重", value=_to_float(current["weight"], 50), step=0.1, key="update_weight")
                meal_rate = st.number_input("食事摂取率", value=_to_float(current["meal_rate"], 80), step=5.0, key="update_meal")
                memo = st.text_area("メモ", value=current["memo"] or "", key="update_memo")
                submitted = st.form_submit_button("更新")
                if submitted:
                    update_health_record(record_id, {
                        "user_id": user_map[user_name],
                        "record_date": record_date.isoformat(),
                        "temperature": temperature,
                        "bp_high": bp_high,
                        "bp_low": bp_low,
                        "pulse": pulse,
                        "spo2": spo2,
                        "weight": weight,
                        "meal_rate": meal_rate,
                        "memo": memo,
                    }, fid)
                    st.success("更新しました。")
                    st.rerun()

    with tab4:
        st.subheader("削除")
        rows = list_health_records(fid, limit=200)
        if not rows:
            st.info("削除できる記録がありません。")
        else:
            labels = [f'{r["id"]}｜{r["record_date"]}｜{r["user_name"]}' for r in rows]
            selected = st.selectbox("削除する記録", labels, key="delete_select")
            record_id = int(selected.split("｜")[0])
            st.warning("削除すると元に戻せません。")
            if st.button("この記録を削除する"):
                delete_health_record(record_id, fid)
                st.success("削除しました。")
                st.rerun()
