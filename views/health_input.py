from datetime import date, timedelta
import streamlit as st
from services.health_service import (
    get_user_options, save_health_record, list_health_records,
    update_health_record, delete_health_record, today_input_status
)

def _num(label, value, step=1.0):
    return st.number_input(label, value=float(value), step=float(step))

def render():
    st.title("健康チェック入力")

    tabs = st.tabs(["新規登録", "更新", "削除", "一覧検索", "今日の入力状況"])

    with tabs[0]:
        user_options = get_user_options()
        if not user_options:
            st.warning("先に「利用者登録」から利用者を登録してください。")
        else:
            with st.form("health_create_form"):
                record_date = st.date_input("記録日", value=date.today())
                user_label = st.selectbox("利用者名", list(user_options.keys()))
                temperature = st.number_input("体温", value=36.5, step=0.1)
                blood_pressure_high = st.number_input("血圧 上", value=120.0, step=1.0)
                blood_pressure_low = st.number_input("血圧 下", value=70.0, step=1.0)
                pulse = st.number_input("脈拍", value=70.0, step=1.0)
                spo2 = st.number_input("SpO2", value=96.0, step=1.0)
                weight = st.number_input("体重", value=50.0, step=0.1)
                meal_rate = st.number_input("食事摂取率", value=80.0, step=5.0)
                memo = st.text_area("メモ")
                submitted = st.form_submit_button("登録")
                if submitted:
                    save_health_record(
                        user_id=user_options[user_label],
                        record_date=record_date,
                        temperature=temperature,
                        blood_pressure_high=blood_pressure_high,
                        blood_pressure_low=blood_pressure_low,
                        pulse=pulse,
                        spo2=spo2,
                        weight=weight,
                        meal_rate=meal_rate,
                        memo=memo,
                    )
                    st.success("健康チェックを登録しました。")
                    st.rerun()

    with tabs[1]:
        st.subheader("記録を選んで更新")
        df = list_health_records(limit=200)
        if df.empty:
            st.info("更新できる記録がありません。")
        else:
            options = {
                f"{row['id']}｜{row['record_date']}｜{row['user_name']}": int(row["id"])
                for _, row in df.iterrows()
            }
            selected = st.selectbox("更新する記録", list(options.keys()), key="update_select")
            rec = df[df["id"] == options[selected]].iloc[0]
            with st.form("health_update_form"):
                record_date = st.date_input("記録日", value=rec["record_date"], key="upd_date")
                temperature = st.number_input("体温", value=float(rec.get("temperature") or 36.5), step=0.1, key="upd_temp")
                blood_pressure_high = st.number_input("血圧 上", value=float(rec.get("blood_pressure_high") or 120), step=1.0, key="upd_bph")
                blood_pressure_low = st.number_input("血圧 下", value=float(rec.get("blood_pressure_low") or 70), step=1.0, key="upd_bpl")
                pulse = st.number_input("脈拍", value=float(rec.get("pulse") or 70), step=1.0, key="upd_pulse")
                spo2 = st.number_input("SpO2", value=float(rec.get("spo2") or 96), step=1.0, key="upd_spo2")
                weight = st.number_input("体重", value=float(rec.get("weight") or 50), step=0.1, key="upd_weight")
                meal_rate = st.number_input("食事摂取率", value=float(rec.get("meal_rate") or 80), step=5.0, key="upd_meal")
                memo = st.text_area("メモ", value=str(rec.get("memo") or ""), key="upd_memo")
                submitted = st.form_submit_button("更新する")
                if submitted:
                    update_health_record(
                        options[selected],
                        record_date=record_date,
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
        st.subheader("記録を選んで削除")
        df = list_health_records(limit=200)
        if df.empty:
            st.info("削除できる記録がありません。")
        else:
            options = {
                f"{row['id']}｜{row['record_date']}｜{row['user_name']}｜体温{row.get('temperature')}": int(row["id"])
                for _, row in df.iterrows()
            }
            selected = st.selectbox("削除する記録", list(options.keys()), key="delete_select")
            st.warning("削除すると元に戻せません。")
            if st.button("この記録を削除する", type="primary"):
                delete_health_record(options[selected])
                st.success("削除しました。")
                st.rerun()

    with tabs[3]:
        st.subheader("一覧検索")
        c1, c2, c3 = st.columns(3)
        with c1:
            keyword = st.text_input("利用者名検索", "")
        with c2:
            start_date = st.date_input("開始日", value=date.today() - timedelta(days=30))
        with c3:
            end_date = st.date_input("終了日", value=date.today())
        df = list_health_records(keyword=keyword, start_date=start_date, end_date=end_date, limit=500)
        if df.empty:
            st.info("該当する記録がありません。")
        else:
            st.dataframe(df, use_container_width=True, hide_index=True)

    with tabs[4]:
        st.subheader("今日の入力状況")
        target_date = st.date_input("確認日", value=date.today(), key="status_date")
        status = today_input_status(target_date)
        if status.empty:
            st.info("利用者がまだ登録されていません。")
        else:
            st.dataframe(status, use_container_width=True, hide_index=True)
