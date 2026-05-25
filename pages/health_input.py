
from __future__ import annotations
import streamlit as st
import pandas as pd
from services.users_service import user_options
from services.health_service import create_health_record, search_health_records, update_health_record, delete_health_record
from utils.time_utils import today_jst
from utils.text_utils import safe_float, safe_int

def _user_label_map():
    options = user_options()
    return {u["user_name"]: u["id"] for u in options}

def render(current_user: dict):
    st.header("健康チェック入力")
    st.caption("体重は任意です。未測定の日は空欄のままで大丈夫です。")
    user_labels = _user_label_map()
    if not user_labels:
        st.warning("利用者マスタを先に登録してください。")
        return

    tab_input, tab_manage = st.tabs(["入力", "検索・更新・削除"])

    with tab_input:
        with st.form("health_form"):
            record_date = st.date_input("記録日", value=today_jst())
            user_name = st.selectbox("利用者", list(user_labels.keys()))
            user_id = user_labels[user_name]
            c1,c2,c3,c4 = st.columns(4)
            temperature = c1.number_input("体温", min_value=30.0, max_value=45.0, value=36.5, step=0.1)
            bp_high = c2.number_input("血圧上", min_value=0, max_value=250, value=120, step=1)
            bp_low = c3.number_input("血圧下", min_value=0, max_value=180, value=70, step=1)
            pulse = c4.number_input("脈拍", min_value=0, max_value=220, value=70, step=1)
            c5,c6,c7 = st.columns(3)
            spo2 = c5.number_input("SpO2", min_value=0, max_value=100, value=96, step=1)
            weight_text = c6.text_input("体重（任意）", placeholder="未測定なら空欄")
            water_ml = c7.number_input("水分摂取量ml（任意）", min_value=0, max_value=5000, value=0, step=50)
            c8,c9,c10 = st.columns(3)
            breakfast = c8.slider("朝食摂取率", 0, 100, 80)
            lunch = c9.slider("昼食摂取率", 0, 100, 80)
            dinner = c10.slider("夕食摂取率", 0, 100, 80)
            family_note = st.text_area("家族共有メモ", placeholder="共有したいことを短く記録")
            change_note = st.text_area("気になる変化", placeholder="事実・気づき・次に見ることを責めずに記録")
            submitted = st.form_submit_button("健康チェックを保存", type="primary", use_container_width=True)
        if submitted:
            create_health_record({
                "record_date": record_date,
                "user_id": user_id,
                "temperature": temperature,
                "bp_high": int(bp_high),
                "bp_low": int(bp_low),
                "pulse": int(pulse),
                "spo2": int(spo2),
                "weight": safe_float(weight_text, None),
                "water_ml": int(water_ml),
                "breakfast": int(breakfast),
                "lunch": int(lunch),
                "dinner": int(dinner),
                "family_note": family_note,
                "change_note": change_note,
            }, current_user)
            st.success("保存しました。")
            st.rerun()

    with tab_manage:
        st.subheader("健康記録の検索")
        c1,c2,c3,c4 = st.columns(4)
        start = c1.date_input("開始日", value=None, key="h_start")
        end = c2.date_input("終了日", value=today_jst(), key="h_end")
        uname = c3.selectbox("利用者", ["全員"] + list(user_labels.keys()), key="h_user")
        keyword = c4.text_input("キーワード", key="h_kw")
        uid = "" if uname == "全員" else user_labels[uname]
        df = search_health_records(start, end, uid, keyword)
        st.dataframe(df[["id","record_date","user_name","temperature","bp_high","bp_low","pulse","spo2","weight","updated_at"]] if not df.empty else df, use_container_width=True, hide_index=True)

        if df.empty:
            return
        st.subheader("選択した健康記録を更新・削除")
        target_label = st.selectbox("対象ID", [f"ID {i+1} | {r['record_date']} | {r['user_name']} | {r['id']}" for i,r in df.iterrows()], key="h_target")
        record_id = target_label.split("|")[-1].strip()
        rec = df[df["id"] == record_id].iloc[0].to_dict()
        token = str(rec.get("updated_at"))

        with st.form("health_update_form"):
            c1,c2,c3,c4 = st.columns(4)
            temperature = c1.number_input("体温", value=float(rec.get("temperature") or 0), step=0.1, key="hu_temp")
            bp_high = c2.number_input("血圧上", value=int(rec.get("bp_high") or 0), step=1, key="hu_bph")
            bp_low = c3.number_input("血圧下", value=int(rec.get("bp_low") or 0), step=1, key="hu_bpl")
            pulse = c4.number_input("脈拍", value=int(rec.get("pulse") or 0), step=1, key="hu_pulse")
            c5,c6,c7 = st.columns(3)
            spo2 = c5.number_input("SpO2", value=int(rec.get("spo2") or 0), step=1, key="hu_spo2")
            weight = c6.text_input("体重（任意）", value="" if pd.isna(rec.get("weight")) or rec.get("weight") is None else str(rec.get("weight")), key="hu_weight")
            water_ml = c7.number_input("水分摂取量ml", value=int(rec.get("water_ml") or 0), step=50, key="hu_water")
            family_note = st.text_area("家族共有メモ", value=str(rec.get("family_note") or ""), key="hu_family")
            change_note = st.text_area("気になる変化", value=str(rec.get("change_note") or ""), key="hu_change")
            colu, cold = st.columns(2)
            do_update = colu.form_submit_button("更新する", type="primary", use_container_width=True)
            do_delete = cold.form_submit_button("削除する", use_container_width=True)
        if do_update:
            try:
                update_health_record(record_id, {
                    "temperature": temperature, "bp_high": int(bp_high), "bp_low": int(bp_low), "pulse": int(pulse),
                    "spo2": int(spo2), "weight": safe_float(weight, None), "water_ml": int(water_ml),
                    "family_note": family_note, "change_note": change_note,
                }, current_user, token)
                st.success("更新しました。")
                st.rerun()
            except Exception as e:
                st.error(str(e))
        if do_delete:
            try:
                delete_health_record(record_id, current_user, token)
                st.success("削除しました。")
                st.rerun()
            except Exception as e:
                st.error(str(e))
