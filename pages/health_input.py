from __future__ import annotations

import streamlit as st
import pandas as pd

from services.users_service import list_user_options
from services.health_service import (
    upsert_health_record,
    list_health_records,
    latest_weight_by_user,
    search_health_records,
    get_health_record,
    update_health_record,
    delete_health_record,
)
from services.audit_service import add_audit_log
from utils.time_utils import today_jst
from utils.text_utils import safe_float, safe_int
from components.ui import header


def _user_label_map():
    options = list_user_options()
    return {name: uid for uid, name in options}


def render(current_user: dict):
    header("健康チェック入力", "体重は任意です。未測定の日は空欄のままで大丈夫です。")
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
            latest_weight = latest_weight_by_user(user_id)
            if latest_weight:
                st.caption(f"最新体重：{latest_weight.weight}kg（{latest_weight.record_date} 測定）")
            else:
                st.caption("最新体重：未測定")

            c1, c2, c3, c4 = st.columns(4)
            temperature = c1.number_input("体温", min_value=30.0, max_value=45.0, value=36.5, step=0.1)
            bp_high = c2.number_input("血圧上", min_value=0, max_value=250, value=120, step=1)
            bp_low = c3.number_input("血圧下", min_value=0, max_value=180, value=70, step=1)
            pulse = c4.number_input("脈拍", min_value=0, max_value=220, value=70, step=1)

            c5, c6, c7 = st.columns(3)
            spo2 = c5.number_input("SpO2", min_value=0, max_value=100, value=96, step=1)
            weight_raw = c6.text_input("体重（任意）", placeholder="未測定なら空欄")
            water_ml = c7.number_input("水分摂取量ml（任意）", min_value=0, max_value=5000, value=0, step=50)

            c8, c9, c10 = st.columns(3)
            breakfast = c8.slider("朝食摂取率", 0, 100, 80, 10)
            lunch = c9.slider("昼食摂取率", 0, 100, 80, 10)
            dinner = c10.slider("夕食摂取率", 0, 100, 80, 10)

            family_note = st.text_area("家族共有メモ", placeholder="共有したいことを短く記録")
            change_note = st.text_area("気になる変化", placeholder="事実・気づき・次に見ることを責めずに記録")
            submitted = st.form_submit_button("健康チェックを保存", type="primary", use_container_width=True)

        if submitted:
            data = {
                "record_date": record_date,
                "user_id": user_id,
                "temperature": float(temperature),
                "bp_high": int(bp_high),
                "bp_low": int(bp_low),
                "pulse": int(pulse),
                "spo2": int(spo2),
                "weight": safe_float(weight_raw, None),
                "breakfast_rate": int(breakfast),
                "lunch_rate": int(lunch),
                "dinner_rate": int(dinner),
                "water_ml": safe_int(water_ml, None),
                "family_note": family_note,
                "change_note": change_note,
                "input_by": current_user.get("display_name", ""),
            }
            upsert_health_record(data)
            add_audit_log(current_user.get("login_id"), current_user.get("role"), "健康チェック保存", "health_records", summary=f"{record_date} {user_name}")
            st.success("保存しました。")
            st.rerun()

        st.subheader("最近の健康記録")
        rows = list_health_records(limit=100)
        if rows:
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    with tab_manage:
        st.subheader("健康記録の検索")
        c1, c2, c3, c4 = st.columns(4)
        date_from = c1.date_input("開始日", value=None, key="health_search_from")
        date_to = c2.date_input("終了日", value=today_jst(), key="health_search_to")
        user_choice = c3.selectbox("利用者", ["全員"] + list(user_labels.keys()), key="health_search_user")
        keyword = c4.text_input("キーワード", key="health_search_keyword")

        target_user_id = None if user_choice == "全員" else user_labels[user_choice]
        results = search_health_records(target_user_id, date_from, date_to, keyword, limit=500)

        if not results:
            st.info("該当する健康記録はありません。")
            return

        df = pd.DataFrame(results)
        st.dataframe(df, use_container_width=True, hide_index=True)

        st.divider()
        st.subheader("選択した健康記録を更新・削除")
        id_options = [int(r["ID"]) for r in results if r.get("ID")]
        selected_id = st.selectbox("対象ID", id_options, format_func=lambda x: f"ID {x}")

        selected = get_health_record(selected_id)
        if not selected:
            st.warning("対象記録が見つかりません。")
            return

        with st.form("health_update_form"):
            c1, c2, c3, c4 = st.columns(4)
            temperature = c1.number_input("体温", min_value=30.0, max_value=45.0, value=float(selected.get("体温") or 36.5), step=0.1)
            bp_high = c2.number_input("血圧上", min_value=0, max_value=250, value=int(selected.get("血圧上") or 0), step=1)
            bp_low = c3.number_input("血圧下", min_value=0, max_value=180, value=int(selected.get("血圧下") or 0), step=1)
            pulse = c4.number_input("脈拍", min_value=0, max_value=220, value=int(selected.get("脈拍") or 0), step=1)

            c5, c6, c7 = st.columns(3)
            spo2 = c5.number_input("SpO2", min_value=0, max_value=100, value=int(selected.get("SpO2") or 0), step=1)
            weight_raw = c6.text_input("体重（任意）", value="" if selected.get("体重") in [None, ""] else str(selected.get("体重")))
            water_ml = c7.number_input("水分摂取量ml（任意）", min_value=0, max_value=5000, value=int(selected.get("水分ml") or 0), step=50)

            c8, c9, c10 = st.columns(3)
            breakfast = c8.slider("朝食摂取率", 0, 100, int(selected.get("朝食") or 0), 10)
            lunch = c9.slider("昼食摂取率", 0, 100, int(selected.get("昼食") or 0), 10)
            dinner = c10.slider("夕食摂取率", 0, 100, int(selected.get("夕食") or 0), 10)

            family_note = st.text_area("家族共有メモ", value=str(selected.get("家族共有メモ") or ""))
            change_note = st.text_area("気になる変化", value=str(selected.get("気になる変化") or ""))

            update_submitted = st.form_submit_button("この健康記録を更新", type="primary", use_container_width=True)

        if update_submitted:
            update_health_record(selected_id, {
                "temperature": float(temperature),
                "bp_high": int(bp_high),
                "bp_low": int(bp_low),
                "pulse": int(pulse),
                "spo2": int(spo2),
                "weight": safe_float(weight_raw, None),
                "breakfast_rate": int(breakfast),
                "lunch_rate": int(lunch),
                "dinner_rate": int(dinner),
                "water_ml": safe_int(water_ml, None),
                "family_note": family_note,
                "change_note": change_note,
                "input_by": current_user.get("display_name", ""),
            })
            add_audit_log(current_user.get("login_id"), current_user.get("role"), "健康チェック更新", "health_records", selected_id, f"ID {selected_id}")
            st.success("更新しました。")
            st.rerun()

        st.warning("削除は取り消せません。記録の誤入力時だけ使ってください。")
        confirm_delete = st.checkbox("この健康記録を削除することを確認しました", key=f"health_delete_{selected_id}")
        if st.button("この健康記録を削除", type="secondary", use_container_width=True):
            if not confirm_delete:
                st.error("確認チェックを入れてください。")
            else:
                delete_health_record(selected_id)
                add_audit_log(current_user.get("login_id"), current_user.get("role"), "健康チェック削除", "health_records", selected_id, f"ID {selected_id}")
                st.success("削除しました。")
                st.rerun()
