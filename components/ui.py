
from __future__ import annotations
import streamlit as st
from config.settings import APP_NAME, APP_VERSION

def apply_yohaku_style():
    st.markdown("""
    <style>
    [data-testid="stSidebarNav"] { display:none !important; }
    .block-container { padding-top: 3rem; padding-bottom: 4rem; max-width: 1180px; }
    body, .stApp { background: #FFFDF7; }
    h1, h2, h3 { letter-spacing: .03em; }
    div[data-testid="stForm"] {
        background: #FFFFFF;
        border: 1px solid #E8E0D4;
        border-radius: 18px;
        padding: 24px;
        margin: 18px 0 28px 0;
    }
    .stButton>button {
        min-height: 44px;
        border-radius: 12px;
        font-weight: 700;
    }
    .stDataFrame { margin-top: 14px; }
    .y-card {
        background: #fff;
        border: 1px solid #E8E0D4;
        border-radius: 18px;
        padding: 20px;
        margin-bottom: 18px;
    }
    .soft-note {
        background: #EEF5FF;
        border-radius: 12px;
        padding: 14px 16px;
        margin: 12px 0 20px 0;
    }
    </style>
    """, unsafe_allow_html=True)

def app_sidebar():
    st.sidebar.markdown(f"### {APP_NAME}")
    st.sidebar.caption(APP_VERSION)
    st.sidebar.divider()
