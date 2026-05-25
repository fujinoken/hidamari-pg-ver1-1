from __future__ import annotations

import streamlit as st
import pandas as pd

from services.users_service import list_user_options
from services.excretion_service import (
    upsert_excretion_record,
    list_excretion_records,
    search_excretion_records,
    get_excretion_record,
    update_excretion_record,
    delete_excretion_record,
)
from services.audit_service import add_audit_log
from utils.time_utils import today_jst
from components.ui import header

SLOTS = [("午前", "9時〜12時"), ("午後", "12時〜15時"), ("夕方", "15時〜17時"), ("夜", "18時〜22時"), ("深夜", "22時〜5時"), ("朝方", "5時〜8時")]
URINE_AMOUNT_OPTIONS = ["なし", "少", "中", "大"]
URINE_TYPE_OPTIONS = ["なし", "普通尿", "濃縮尿"]
STOOL_AMOUNT_OPTIONS = ["なし", "少", "中", "大"]
STOOL_TYPE_OPTIONS = ["なし", "普通便", "硬便", "下痢便", "水様便"]


def _user_label_map():
    options = list_user_options()
    return {name: uid for uid, name in options}


def _index(options, value):
    try:
        return options.index(value)
    except Exception:
        return 0


def render(current_user: dict):
    header("排泄チェック入力", "細かすぎる時刻入力ではなく、時間帯で現場に合う記録にします。")
    user_labels = _user_label_map()
    if not user_labels:
        st.warning("利用者マスタを先に登録してください。")
        return

    tab_input, tab_manage = st.tabs(["入力", "検索・更新・削除"])

    with tab_input:
        with st.form("excretion_form"):
            record_date = st.date_input("記録日", value=today_jst())
            user_name = st.selectbox("利用者", list(user_labels.keys()))
            slot = st.selectbox("時間帯", [x[0] for x in SLOTS])
            slot_hint = dict(SLOTS).get(slot, "")
            st.caption(f"目安：{slot_hint}")
            c1, c2, c3, c4 = st.columns(4)
            urine_amount = c1.selectbox("尿量", URINE_AMOUNT_OPTIONS)
            urine_type = c2.selectbox("尿性状", URINE_TYPE_OPTIONS)
            stool_amount = c3.selectbox("便量", STOOL_AMOUNT_OPTIONS)
            stool_type = c4.selectbox("便性状", STOOL_TYPE_OPTIONS)
            memo = st.text_area("排泄メモ", placeholder="確認した事実だけを短く記録")
            submitted = st.form_submit_button("排泄チェックを保存", type="primary", use_container_width=True)

        if submitted:
            upsert_excretion_record({
                "record_date": record_date,
                "user_id": user_labels[user_name],
                "slot": slot,
                "slot_hint": slot_hint,
                "urine_amount": urine_amount,
                "urine_type": urine_type,
                "stool_amount": stool_amount,
                "stool_type": stool_type,
                "memo": memo,
                "input_by": current_user.get("display_name", ""),
            })
            add_audit_log(current_user.get("login_id"), current_user.get("role"), "排泄チェック保存", "excretion_records", summary=f"{record_date} {user_name} {slot}")
            st.success("保存しました。")
            st.rerun()

        st.subheader("最近の排泄記録")
        rows = list_excretion_records(limit=100)
        if rows:
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    with tab_manage:
        st.subheader("排泄記録の検索")
        c1, c2, c3, c4 = st.columns(4)
        date_from = c1.date_input("開始日", value=None, key="excretion_search_from")
        date_to = c2.date_input("終了日", value=today_jst(), key="excretion_search_to")
        user_choice = c3.selectbox("利用者", ["全員"] + list(user_labels.keys()), key="excretion_search_user")
        keyword = c4.text_input("キーワード", key="excretion_search_keyword")

        target_user_id = None if user_choice == "全員" else user_labels[user_choice]
        results = search_excretion_records(target_user_id, date_from, date_to, keyword, limit=500)

        if not results:
            st.info("該当する排泄記録はありません。")
            return

        df = pd.DataFrame(results)
        st.dataframe(df, use_container_width=True, hide_index=True)

        st.divider()
        st.subheader("選択した排泄記録を更新・削除")
        id_options = [int(r["ID"]) for r in results if r.get("ID")]
        selected_id = st.selectbox("対象ID", id_options, format_func=lambda x: f"ID {x}")

        selected = get_excretion_record(selected_id)
        if not selected:
            st.warning("対象記録が見つかりません。")
            return

        with st.form("excretion_update_form"):
            slot = st.selectbox("時間帯", [x[0] for x in SLOTS], index=_index([x[0] for x in SLOTS], selected.get("時間帯")))
            slot_hint = dict(SLOTS).get(slot, "")
            st.caption(f"目安：{slot_hint}")

            c1, c2, c3, c4 = st.columns(4)
            urine_amount = c1.selectbox("尿量", URINE_AMOUNT_OPTIONS, index=_index(URINE_AMOUNT_OPTIONS, selected.get("尿量")))
            urine_type = c2.selectbox("尿性状", URINE_TYPE_OPTIONS, index=_index(URINE_TYPE_OPTIONS, selected.get("尿性状")))
            stool_amount = c3.selectbox("便量", STOOL_AMOUNT_OPTIONS, index=_index(STOOL_AMOUNT_OPTIONS, selected.get("便量")))
            stool_type = c4.selectbox("便性状", STOOL_TYPE_OPTIONS, index=_index(STOOL_TYPE_OPTIONS, selected.get("便性状")))
            memo = st.text_area("排泄メモ", value=str(selected.get("メモ") or ""))

            update_submitted = st.form_submit_button("この排泄記録を更新", type="primary", use_container_width=True)

        if update_submitted:
            update_excretion_record(selected_id, {
                "slot": slot,
                "slot_hint": slot_hint,
                "urine_amount": urine_amount,
                "urine_type": urine_type,
                "stool_amount": stool_amount,
                "stool_type": stool_type,
                "memo": memo,
                "input_by": current_user.get("display_name", ""),
            })
            add_audit_log(current_user.get("login_id"), current_user.get("role"), "排泄チェック更新", "excretion_records", selected_id, f"ID {selected_id}")
            st.success("更新しました。")
            st.rerun()

        st.warning("削除は取り消せません。記録の誤入力時だけ使ってください。")
        confirm_delete = st.checkbox("この排泄記録を削除することを確認しました", key=f"excretion_delete_{selected_id}")
        if st.button("この排泄記録を削除", type="secondary", use_container_width=True):
            if not confirm_delete:
                st.error("確認チェックを入れてください。")
            else:
                delete_excretion_record(selected_id)
                add_audit_log(current_user.get("login_id"), current_user.get("role"), "排泄チェック削除", "excretion_records", selected_id, f"ID {selected_id}")
                st.success("削除しました。")
                st.rerun()
