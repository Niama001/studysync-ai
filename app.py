"""
StudySync -- a small study-session app.

Ships complete from Week 2. Each tinker below is a real ticket against this
running app: a scoped, working feature with one part that isn't finished yet.

Run with: streamlit run app.py
"""

import streamlit as st

from scoring import render_session_scorer_tab
from sessions import render_session_log_tab
from rag.ui import render_ai_study_spot_tab

st.set_page_config(page_title="StudySync", page_icon="📚")
st.title("📚 StudySync")
st.caption("A small study-session app, built one ticket at a time.")

tab1, tab2, tab3 = st.tabs(["Session Scorer", "Session Log", "AI Study Spot Advisor"])

with tab1:
    render_session_scorer_tab()

with tab2:
    render_session_log_tab()

with tab3:
    render_ai_study_spot_tab()