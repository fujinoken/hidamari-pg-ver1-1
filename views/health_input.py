import datetime as dt
import streamlit as st
from services.health_service import list_users, save_health_record, list_health_records, update_health_record, delete_health_record, today_input_status


def _record_form(prefix: str, default: dict | None = None):
    default = default or {}
    users = list_users()
    if users.empty:
        st.warning("先に『利用者登録』で利用者を登録してください。")
        return None
    user_options = dict(zip(users["user_name"], users["id"]))
    default_user_name = None
    if default.get("user_id"):
        for name, uid in user_options.items():
            if str(uid) == str(default.get("user_id")):
                default_user_name = name
                break
    user_name = st.selectbox("利用者名", list(user_options.keys()), index=list(user_options.keys()).index(default_user_name) if default_user_name in user_options else 0, key=f"{prefix}_user")
    record_date = st.date_input("記録日", value=dt.date.fromisoformat(default.get("record_date")) if default.get("record_date") else dt.date.today(), key=f"{prefix}_date")
    c1, c2, c3 = st.columns(3)
    with c1:
        temperature = st.number_input("体温", min_value=30.0, max_value=45.0, value=float(default.get("temperature") or 36.5), step=0.1, key=f"{prefix}_temp")
        bp_high = st.number_input("血圧 上", min_value=0.0, max_value=250.0, value=float(default.get("bp_high") or 120), step=1.0, key=f"{prefix}_bph")
        bp_low = st.number_input("血圧 下", min_value=0.0, max_value=200.0, value=float(default.get("bp_low") or 70), step=1.0, key=f"{prefix}_bpl")
    with c2:
        pulse = st.number_input("脈拍", min_value=0.0, max_value=250.0, value=float(default.get("pulse") or 70), step=1.0, key=f"{prefix}_pulse")
        spo2 = st.number_input("SpO2", min_value=0.0, max_value=100.0, value=float(default.get("spo2") or 96), step=1.0, key=f"{prefix}_spo2")
    with c3:
        weight = st.number_input("体重", min_value=0.0, max_value=200.0, value=float(default.get("weight") or 50), step=0.1, key=f"{prefix}_weight")
        meal_rate = st.number_input("食事摂取率", min_value=0.0, max_value=100.0, value=float(default.get("meal_rate") or 80), step=1.0, key=f"{prefix}_meal")
    memo = st.text_area("メモ", value=str(default.get("memo") or ""), key=f"{prefix}_memo")
    return {
        "user_id": user_options[user_name],
        "record_date": record_date.isoformat(),
        "temperature": temperature,
        "bp_high": bp_high,
        "bp_low": bp_low,
        "pulse": pulse,
        "spo2": spo2,
        "weight": weight,
        "meal_rate": meal_rate,
        "memo": memo,
    }


def render():
    st.title("健康チェック入力")
    tabs = st.tabs(["登録", "更新", "削除", "一覧検索", "今日の入力状況"])

    with tabs[0]:
        st.subheader("健康チェック保存")
        with st.form("create_health"):
            data = _record_form("create")
            submitted = st.form_submit_button("保存")
        if submitted and data:
            try:
                save_health_record(data)
                st.success("保存しました。同じ利用者・同じ日付は上書き保存されます。")
                st.rerun()
            except Exception as e:
                st.error(f"保存エラー: {e}")

    with tabs[1]:
        st.subheader("更新")
        df = list_health_records()
        if df.empty:
            st.info("更新できる記録がありません。")
        else:
            labels = [f"{r.record_date}｜{r.user_name}｜{r.id}" for r in df.itertuples()]
            selected = st.selectbox("更新する記録", labels)
            rec_id = selected.split("｜")[-1]
            rec = df[df["id"].astype(str) == rec_id].iloc[0].to_dict()
            with st.form("update_health"):
                data = _record_form("update", rec)
                submitted = st.form_submit_button("更新")
            if submitted and data:
                try:
                    update_health_record(rec_id, data)
                    st.success("更新しました。")
                    st.rerun()
                except Exception as e:
                    st.error(f"更新エラー: {e}")

    with tabs[2]:
        st.subheader("削除")
        df = list_health_records()
        if df.empty:
            st.info("削除できる記録がありません。")
        else:
            labels = [f"{r.record_date}｜{r.user_name}｜{r.id}" for r in df.itertuples()]
            selected = st.selectbox("削除する記録", labels, key="delete_select")
            rec_id = selected.split("｜")[-1]
            st.warning("削除すると元に戻せません。")
            if st.button("この記録を削除する"):
                try:
                    delete_health_record(rec_id)
                    st.success("削除しました。")
                    st.rerun()
                except Exception as e:
                    st.error(f"削除エラー: {e}")

    with tabs[3]:
        st.subheader("一覧検索")
        c1, c2 = st.columns(2)
        with c1:
            start = st.date_input("開始日", value=dt.date.today().replace(day=1))
        with c2:
            end = st.date_input("終了日", value=dt.date.today())
        users = list_users()
        user_filter = None
        if not users.empty:
            options = ["全員"] + list(users["user_name"])
            name = st.selectbox("利用者", options)
            if name != "全員":
                user_filter = users.loc[users["user_name"] == name, "id"].iloc[0]
        df = list_health_records(start.isoformat(), end.isoformat(), user_filter)
        st.dataframe(df, use_container_width=True, hide_index=True)

    with tabs[4]:
        st.subheader("今日の入力状況")
        target = st.date_input("確認日", value=dt.date.today(), key="status_date")
        df = today_input_status(target.isoformat())
        st.dataframe(df, use_container_width=True, hide_index=True)
