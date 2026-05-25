
from __future__ import annotations
import streamlit as st
from services.users_service import user_options
from services.excretion_service import create_excretion_record, search_excretion_records, update_excretion_record, delete_excretion_record
from utils.time_utils import today_jst

URINE_AMOUNT=["なし","少","中","大"]
URINE_TYPE=["なし","普通尿","濃縮尿"]
STOOL_AMOUNT=["なし","少","中","大"]
STOOL_TYPE=["なし","普通便","下痢便","水様便"]
SLOTS=["午前","午後","夕方","夜","深夜","朝方"]

def _user_label_map():
    return {u["user_name"]: u["id"] for u in user_options()}

def render(current_user: dict):
    st.header("排泄チェック入力")
    user_labels=_user_label_map()
    if not user_labels:
        st.warning("利用者マスタを先に登録してください。")
        return
    tab_input, tab_manage=st.tabs(["入力","検索・更新・削除"])

    with tab_input:
        with st.form("excretion_form"):
            record_date=st.date_input("記録日", value=today_jst())
            user_name=st.selectbox("利用者", list(user_labels.keys()))
            time_slot=st.selectbox("時間帯", SLOTS)
            c1,c2,c3,c4=st.columns(4)
            urine_amount=c1.selectbox("尿量", URINE_AMOUNT)
            urine_type=c2.selectbox("尿性状", URINE_TYPE)
            stool_amount=c3.selectbox("便量", STOOL_AMOUNT)
            stool_type=c4.selectbox("便性状", STOOL_TYPE)
            memo=st.text_area("排泄メモ", placeholder="確認した事実だけを短く記録")
            submitted=st.form_submit_button("排泄チェックを保存", type="primary", use_container_width=True)
        if submitted:
            create_excretion_record({
                "record_date":record_date,"user_id":user_labels[user_name],"time_slot":time_slot,
                "urine_amount":urine_amount,"urine_type":urine_type,"stool_amount":stool_amount,"stool_type":stool_type,"memo":memo,
            }, current_user)
            st.success("保存しました。")
            st.rerun()

    with tab_manage:
        st.subheader("排泄記録の検索")
        c1,c2,c3,c4=st.columns(4)
        start=c1.date_input("開始日", value=None, key="e_start")
        end=c2.date_input("終了日", value=today_jst(), key="e_end")
        uname=c3.selectbox("利用者", ["全員"]+list(user_labels.keys()), key="e_user")
        keyword=c4.text_input("キーワード", key="e_kw")
        uid="" if uname=="全員" else user_labels[uname]
        df=search_excretion_records(start,end,uid,keyword)
        st.dataframe(df[["id","record_date","user_name","time_slot","urine_amount","urine_type","stool_amount","stool_type","memo","updated_at"]] if not df.empty else df, use_container_width=True, hide_index=True)
        if df.empty: return
        st.subheader("選択した排泄記録を更新・削除")
        target=st.selectbox("対象ID", [f"ID {i+1} | {r['record_date']} | {r['user_name']} | {r['time_slot']} | {r['id']}" for i,r in df.iterrows()], key="e_target")
        record_id=target.split("|")[-1].strip()
        rec=df[df["id"]==record_id].iloc[0].to_dict()
        token=str(rec.get("updated_at"))
        with st.form("excretion_update_form"):
            c1,c2,c3,c4=st.columns(4)
            urine_amount=c1.selectbox("尿量", URINE_AMOUNT, index=URINE_AMOUNT.index(rec.get("urine_amount") or "なし"), key="eu_ua")
            urine_type=c2.selectbox("尿性状", URINE_TYPE, index=URINE_TYPE.index(rec.get("urine_type") or "なし"), key="eu_ut")
            stool_amount=c3.selectbox("便量", STOOL_AMOUNT, index=STOOL_AMOUNT.index(rec.get("stool_amount") or "なし"), key="eu_sa")
            stool_type=c4.selectbox("便性状", STOOL_TYPE, index=STOOL_TYPE.index(rec.get("stool_type") or "なし"), key="eu_st")
            memo=st.text_area("排泄メモ", value=str(rec.get("memo") or ""), key="eu_memo")
            colu,cold=st.columns(2)
            do_update=colu.form_submit_button("更新する", type="primary", use_container_width=True)
            do_delete=cold.form_submit_button("削除する", use_container_width=True)
        if do_update:
            try:
                update_excretion_record(record_id, {"urine_amount":urine_amount,"urine_type":urine_type,"stool_amount":stool_amount,"stool_type":stool_type,"memo":memo}, current_user, token)
                st.success("更新しました。")
                st.rerun()
            except Exception as e:
                st.error(str(e))
        if do_delete:
            try:
                delete_excretion_record(record_id, current_user, token)
                st.success("削除しました。")
                st.rerun()
            except Exception as e:
                st.error(str(e))
