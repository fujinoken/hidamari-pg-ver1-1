from __future__ import annotations

import streamlit as st
import pandas as pd

from services.handover_service import (
    create_handover,
    list_handovers,
    search_handovers,
    get_handover,
    update_handover,
    delete_handover,
)
from services.audit_service import add_audit_log
from utils.time_utils import today_jst
from components.ui import header


SHIFT_OPTIONS = ["日勤", "夜勤"]
PRIORITY_OPTIONS = ["通常", "観察", "注意", "至急"]
STATUS_OPTIONS = ["観察継続", "一旦様子を見る", "対応中", "完了"]


def _index(options, value):
    try:
        return options.index(value)
    except Exception:
        return 0


def render(current_user: dict):
    header("業務全体申し送り", "事実・気づき・次に見ることを分け、責めない共有にします。")

    tab_input, tab_manage = st.tabs(["入力", "検索・更新・削除"])

    with tab_input:
        with st.form("handover_form"):
            record_date = st.date_input("日付", value=today_jst())
            shift = st.selectbox("勤務帯", SHIFT_OPTIONS)
            writer = st.text_input("記入者", value=current_user.get("display_name", ""))
            fact_text = st.text_area("事実", placeholder="実際に起きたこと・見たこと")
            notice_text = st.text_area("気づき", placeholder="普段との違い、気になったこと")
            next_watch_text = st.text_area("次に見ること", placeholder="次の勤務者が確認するとよいこと")
            priority = st.selectbox("優先度", PRIORITY_OPTIONS)
            status = st.selectbox("状態", STATUS_OPTIONS)
            submitted = st.form_submit_button("申し送りを保存", type="primary", use_container_width=True)

        if submitted:
            row = create_handover({
                "record_date": record_date,
                "shift": shift,
                "writer": writer,
                "fact_text": fact_text,
                "notice_text": notice_text,
                "next_watch_text": next_watch_text,
                "priority": priority,
                "status": status,
            })
            add_audit_log(current_user.get("login_id"), current_user.get("role"), "申し送り保存", "handover_logs", row.id, f"{record_date} {shift}")
            st.success("保存しました。")
            st.rerun()

        st.subheader("最近の申し送り")
        rows = list_handovers(100)
        if rows:
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    with tab_manage:
        st.subheader("申し送りの検索")
        c1, c2, c3, c4 = st.columns(4)
        date_from = c1.date_input("開始日", value=None, key="handover_search_from")
        date_to = c2.date_input("終了日", value=today_jst(), key="handover_search_to")
        shift_choice = c3.selectbox("勤務帯", ["全て"] + SHIFT_OPTIONS, key="handover_search_shift")
        keyword = c4.text_input("キーワード", key="handover_search_keyword")

        target_shift = "" if shift_choice == "全て" else shift_choice
        results = search_handovers(date_from, date_to, keyword, target_shift, limit=500)

        if not results:
            st.info("該当する申し送りはありません。")
            return

        df = pd.DataFrame(results)
        st.dataframe(df, use_container_width=True, hide_index=True)

        st.divider()
        st.subheader("選択した申し送りを更新・削除")
        id_options = [int(r["ID"]) for r in results if r.get("ID")]
        selected_id = st.selectbox("対象ID", id_options, format_func=lambda x: f"ID {x}")

        selected = get_handover(selected_id)
        if not selected:
            st.warning("対象記録が見つかりません。")
            return

        with st.form("handover_update_form"):
            shift = st.selectbox("勤務帯", SHIFT_OPTIONS, index=_index(SHIFT_OPTIONS, selected.get("勤務帯")))
            writer = st.text_input("記入者", value=str(selected.get("記入者") or current_user.get("display_name", "")))
            fact_text = st.text_area("事実", value=str(selected.get("事実") or ""))
            notice_text = st.text_area("気づき", value=str(selected.get("気づき") or ""))
            next_watch_text = st.text_area("次に見ること", value=str(selected.get("次に見ること") or ""))
            priority = st.selectbox("優先度", PRIORITY_OPTIONS, index=_index(PRIORITY_OPTIONS, selected.get("優先度")))
            status = st.selectbox("状態", STATUS_OPTIONS, index=_index(STATUS_OPTIONS, selected.get("状態")))

            update_submitted = st.form_submit_button("この申し送りを更新", type="primary", use_container_width=True)

        if update_submitted:
            update_handover(selected_id, {
                "shift": shift,
                "writer": writer,
                "fact_text": fact_text,
                "notice_text": notice_text,
                "next_watch_text": next_watch_text,
                "priority": priority,
                "status": status,
            })
            add_audit_log(current_user.get("login_id"), current_user.get("role"), "申し送り更新", "handover_logs", selected_id, f"ID {selected_id}")
            st.success("更新しました。")
            st.rerun()

        st.warning("削除は取り消せません。記録の誤入力時だけ使ってください。")
        confirm_delete = st.checkbox("この申し送りを削除することを確認しました", key=f"handover_delete_{selected_id}")
        if st.button("この申し送りを削除", type="secondary", use_container_width=True):
            if not confirm_delete:
                st.error("確認チェックを入れてください。")
            else:
                delete_handover(selected_id)
                add_audit_log(current_user.get("login_id"), current_user.get("role"), "申し送り削除", "handover_logs", selected_id, f"ID {selected_id}")
                st.success("削除しました。")
                st.rerun()
