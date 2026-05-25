import streamlit as st


def render():
    st.header("申し送り")
    st.info("Ver1.3.5ではメニュー整理用の仮ページです。今後、申し送り保存・一覧機能を追加できます。")
    st.text_area("申し送りメモ", height=180, placeholder="例：夜間の様子、食事、排泄、気になる変化など")
    st.button("一時表示のみ（保存機能は未実装）", disabled=True)
