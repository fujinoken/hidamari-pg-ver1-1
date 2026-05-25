from __future__ import annotations

import streamlit as st
from config.settings import APP_NAME, APP_VERSION


def apply_yohaku_style():
    st.markdown(
        """
        <style>
        .stApp { background: #fffdf7; color: #2f2f2f; }
        section.main > div { padding-top: 1.4rem; padding-bottom: 3rem; max-width: 1180px; }
        h1, h2, h3 { letter-spacing: .02em; line-height: 1.55; }
        p, li, label, div { line-height: 1.75; }
        div[data-testid="stMetric"] { background: #ffffff; border: 1px solid #eee6dc; border-radius: 18px; padding: 18px 20px; }
        .y-card { background: #ffffff; border: 1px solid #eee6dc; border-radius: 22px; padding: 22px 24px; margin: 18px 0; }
        .y-note { color: #6f6a63; font-size: .95rem; }
        .stButton > button, .stDownloadButton > button { border-radius: 14px; min-height: 48px; margin-top: 8px; margin-bottom: 8px; }
        div[data-testid="stDataFrame"] { margin-top: 14px; margin-bottom: 22px; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def header(title: str, subtitle: str = ""):
    st.title(title)
    if subtitle:
        st.caption(subtitle)


def app_sidebar():
    st.sidebar.markdown(f"### {APP_NAME}")
    st.sidebar.caption(APP_VERSION)
    st.sidebar.divider()


def card(title: str, body: str = ""):
    st.markdown(f"<div class='y-card'><h3>{title}</h3><p class='y-note'>{body}</p></div>", unsafe_allow_html=True)
