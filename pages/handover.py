
from __future__ import annotations
import streamlit as st
from services.handover_service import create_handover, search_handovers, update_handover, delete_handover
from utils.time_utils import today_jst

def render(current_user: dict):
    st.header("業務全体申し送り")
    st.caption("事実／気づき／次に見ることを分けて記録します。")
    tab_input, tab_manage=st.tabs(["入力","検索・更新・削除"])

    with tab_input:
        with st.form("handover_form"):
            record_date=st.date_input("日付", value=today_jst())
            shift=st.selectbox("勤務帯", ["日勤","夜勤"])
            writer=st.text_input("記入者", value=current_user.get("display_name",""))
            fact=st.text_area("事実", placeholder="実際にあったこと")
            notice=st.text_area("気づき", placeholder="普段との違い、気になったこと")
            next_watch=st.text_area("次に見ること", placeholder="次の勤務者が確認するとよいこと")
            c1,c2=st.columns(2)
            priority=c1.selectbox("優先度", ["通常","注意","至急"])
            status=c2.selectbox("状態", ["観察継続","対応中","完了","一旦様子を見る"])
            submitted=st.form_submit_button("申し送りを保存", type="primary", use_container_width=True)
        if submitted:
            create_handover({"record_date":record_date,"shift":shift,"writer":writer,"fact":fact,"notice":notice,"next_watch":next_watch,"priority":priority,"status":status}, current_user)
            st.success("保存しました。")
            st.rerun()

    with tab_manage:
        st.subheader("申し送りの検索")
        c1,c2,c3=st.columns(3)
        start=c1.date_input("開始日", value=None, key="ho_start")
        end=c2.date_input("終了日", value=today_jst(), key="ho_end")
        keyword=c3.text_input("キーワード", key="ho_kw")
        df=search_handovers(start,end,keyword)
        st.dataframe(df[["id","record_date","shift","writer","fact","notice","next_watch","priority","status","updated_at"]] if not df.empty else df, use_container_width=True, hide_index=True)
        if df.empty: return
        st.subheader("選択した申し送りを更新・削除")
        target=st.selectbox("対象ID", [f"ID {i+1} | {r['record_date']} | {r['shift']} | {r['id']}" for i,r in df.iterrows()], key="ho_target")
        record_id=target.split("|")[-1].strip()
        rec=df[df["id"]==record_id].iloc[0].to_dict()
        token=str(rec.get("updated_at"))
        with st.form("handover_update_form"):
            fact=st.text_area("事実", value=str(rec.get("fact") or ""), key="hou_fact")
            notice=st.text_area("気づき", value=str(rec.get("notice") or ""), key="hou_notice")
            next_watch=st.text_area("次に見ること", value=str(rec.get("next_watch") or ""), key="hou_next")
            c1,c2=st.columns(2)
            priority=c1.selectbox("優先度", ["通常","注意","至急"], index=["通常","注意","至急"].index(rec.get("priority") or "通常"), key="hou_pri")
            status_options=["観察継続","対応中","完了","一旦様子を見る"]
            status=c2.selectbox("状態", status_options, index=status_options.index(rec.get("status") or "観察継続"), key="hou_status")
            colu,cold=st.columns(2)
            do_update=colu.form_submit_button("更新する", type="primary", use_container_width=True)
            do_delete=cold.form_submit_button("削除する", use_container_width=True)
        if do_update:
            try:
                update_handover(record_id, {"fact":fact,"notice":notice,"next_watch":next_watch,"priority":priority,"status":status}, current_user, token)
                st.success("更新しました。")
                st.rerun()
            except Exception as e:
                st.error(str(e))
        if do_delete:
            try:
                delete_handover(record_id, current_user, token)
                st.success("削除しました。")
                st.rerun()
            except Exception as e:
                st.error(str(e))
