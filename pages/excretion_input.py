from __future__ import annotations

import streamlit as st
import pandas as pd
from services.users_service import list_user_options
from services.excretion_service import upsert_excretion_record, list_excretion_records
from services.audit_service import add_audit_log
from utils.time_utils import today_jst
from components.ui import header

SLOTS = [("午前", "9時〜12時"), ("午後", "12時〜15時"), ("夕方", "15時〜17時"), ("夜", "18時〜22時"), ("深夜", "22時〜5時"), ("朝方", "5時〜8時")]


def render(current_user: dict):
    header("排泄チェック入力", "細かすぎる時刻入力ではなく、時間帯で現場に合う記録にします。")
    options = list_user_options()
    if not options:
        st.warning("利用者マスタを先に登録してください。")
        return
    user_labels = {name: uid for uid, name in options}

    with st.form("excretion_form"):
        record_date = st.date_input("記録日", value=today_jst())
        user_name = st.selectbox("利用者", list(user_labels.keys()))
        slot = st.selectbox("時間帯", [x[0] for x in SLOTS])
        slot_hint = dict(SLOTS).get(slot, "")
        st.caption(f"目安：{slot_hint}")
        c1, c2, c3, c4 = st.columns(4)
        urine_amount = c1.selectbox("尿量", ["なし", "少", "中", "大"])
        urine_type = c2.selectbox("尿性状", ["なし", "普通尿", "濃縮尿"])
        stool_amount = c3.selectbox("便量", ["なし", "少", "中", "大"])
        stool_type = c4.selectbox("便性状", ["なし", "普通便", "硬便", "下痢便", "水様便"])
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
    rows = list_excretion_records(limit=200)
    if rows:
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
