import streamlit as st
import pandas as pd
from datetime import date, timedelta
from services.health_service import (
    list_users, save_health_record, list_health_records,
    update_health_record, delete_health_record, get_health_record,
    today_input_status,
)

def _user_options(users):
    return {f"{u['user_name']}（{u.get('room','')}）": u["id"] for u in users}

def render():
    facility_id = st.session_state["facility_id"]
    st.title("健康チェック入力")
    users = list_users(facility_id)

    if not users:
        st.warning("利用者が未登録です。先に「利用者登録」から登録してください。")
        return

    tabs = st.tabs(["新規保存", "更新", "削除", "一覧検索", "今日の入力状況"])

    opts = _user_options(users)

    with tabs[0]:
        st.subheader("健康チェックを保存")
        with st.form("health_create_form", clear_on_submit=True):
            record_date = st.date_input("記録日", value=date.today())
            selected = st.selectbox("利用者名", list(opts.keys()))
            c1, c2, c3 = st.columns(3)
            with c1:
                temperature = st.number_input("体温", 30.0, 45.0, 36.5, 0.1)
                blood_pressure_high = st.number_input("血圧 上", 50.0, 250.0, 120.0, 1.0)
                blood_pressure_low = st.number_input("血圧 下", 30.0, 150.0, 70.0, 1.0)
            with c2:
                pulse = st.number_input("脈拍", 20.0, 220.0, 70.0, 1.0)
                spo2 = st.number_input("SpO2", 50.0, 100.0, 96.0, 1.0)
                weight = st.number_input("体重", 0.0, 200.0, 50.0, 0.1)
            with c3:
                meal_rate = st.number_input("食事摂取率", 0.0, 100.0, 80.0, 1.0)
            memo = st.text_area("メモ")
            submitted = st.form_submit_button("保存")
            if submitted:
                save_health_record(
                    facility_id=facility_id,
                    user_id=opts[selected],
                    record_date=record_date.isoformat(),
                    temperature=temperature,
                    blood_pressure_high=blood_pressure_high,
                    blood_pressure_low=blood_pressure_low,
                    pulse=pulse,
                    spo2=spo2,
                    weight=weight,
                    meal_rate=meal_rate,
                    memo=memo,
                )
                st.success("健康チェックを保存しました。")
                st.rerun()

    with tabs[1]:
        st.subheader("健康チェックを更新")
        records = list_health_records(facility_id, limit=200)
        if not records:
            st.info("更新できる記録がありません。")
        else:
            labels = {
                f"{r['record_date']}｜{r['user_name']}｜体温 {r.get('temperature','')}｜ID:{r['id'][:8]}": r["id"]
                for r in records
            }
            selected_label = st.selectbox("更新する記録", list(labels.keys()), key="update_select")
            rec = get_health_record(labels[selected_label])
            if rec:
                with st.form("health_update_form"):
                    record_date = st.date_input("記録日", value=date.fromisoformat(str(rec["record_date"])))
                    current_user_key = next((k for k,v in opts.items() if str(v)==str(rec["user_id"])), list(opts.keys())[0])
                    selected_user = st.selectbox("利用者名", list(opts.keys()), index=list(opts.keys()).index(current_user_key))
                    c1, c2, c3 = st.columns(3)
                    with c1:
                        temperature = st.number_input("体温", 30.0, 45.0, float(rec.get("temperature") or 36.5), 0.1)
                        blood_pressure_high = st.number_input("血圧 上", 50.0, 250.0, float(rec.get("blood_pressure_high") or 120), 1.0)
                        blood_pressure_low = st.number_input("血圧 下", 30.0, 150.0, float(rec.get("blood_pressure_low") or 70), 1.0)
                    with c2:
                        pulse = st.number_input("脈拍", 20.0, 220.0, float(rec.get("pulse") or 70), 1.0)
                        spo2 = st.number_input("SpO2", 50.0, 100.0, float(rec.get("spo2") or 96), 1.0)
                        weight = st.number_input("体重", 0.0, 200.0, float(rec.get("weight") or 50), 0.1)
                    with c3:
                        meal_rate = st.number_input("食事摂取率", 0.0, 100.0, float(rec.get("meal_rate") or 80), 1.0)
                    memo = st.text_area("メモ", value=rec.get("memo") or "")
                    if st.form_submit_button("更新する"):
                        update_health_record(
                            labels[selected_label],
                            record_date=record_date.isoformat(),
                            user_id=opts[selected_user],
                            temperature=temperature,
                            blood_pressure_high=blood_pressure_high,
                            blood_pressure_low=blood_pressure_low,
                            pulse=pulse,
                            spo2=spo2,
                            weight=weight,
                            meal_rate=meal_rate,
                            memo=memo,
                        )
                        st.success("更新しました。")
                        st.rerun()

    with tabs[2]:
        st.subheader("健康チェックを削除")
        records = list_health_records(facility_id, limit=200)
        if not records:
            st.info("削除できる記録がありません。")
        else:
            labels = {
                f"{r['record_date']}｜{r['user_name']}｜体温 {r.get('temperature','')}｜ID:{r['id'][:8]}": r["id"]
                for r in records
            }
            selected_label = st.selectbox("削除する記録", list(labels.keys()), key="delete_select")
            st.warning("削除すると元に戻せません。")
            if st.button("この記録を削除する", type="primary"):
                delete_health_record(labels[selected_label])
                st.success("削除しました。")
                st.rerun()

    with tabs[3]:
        st.subheader("一覧検索")
        c1, c2, c3 = st.columns(3)
        with c1:
            start = st.date_input("開始日", value=date.today() - timedelta(days=30), key="search_start")
        with c2:
            end = st.date_input("終了日", value=date.today(), key="search_end")
        with c3:
            search_user = st.selectbox("利用者", ["全員"] + list(opts.keys()), key="search_user")
        keyword = st.text_input("キーワード（メモ・氏名）")
        user_id = None if search_user == "全員" else opts[search_user]
        rows = list_health_records(facility_id, start.isoformat(), end.isoformat(), user_id, keyword, limit=500)
        if rows:
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
            st.download_button(
                "CSVダウンロード",
                pd.DataFrame(rows).to_csv(index=False).encode("utf-8-sig"),
                file_name="health_records.csv",
                mime="text/csv",
            )
        else:
            st.info("該当する記録はありません。")

    with tabs[4]:
        st.subheader("今日の入力状況")
        target_date = st.date_input("確認日", value=date.today(), key="status_date")
        rows = today_input_status(facility_id, target_date.isoformat())
        if rows:
            df = pd.DataFrame(rows)
            st.dataframe(df[["user_name", "room", "status"]], use_container_width=True, hide_index=True)
            done = (df["status"] == "入力済み").sum()
            st.info(f"入力済み：{done}名 / 対象：{len(df)}名")
        else:
            st.info("利用者が登録されていません。")
