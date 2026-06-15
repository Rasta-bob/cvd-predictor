from __future__ import annotations

import streamlit as st

from backend.storage import init_db
from frontend.about import render_about
from frontend.auth import login_panel
from frontend.contact import render_contact
from frontend.dashboard import render_dashboard, render_reports
from frontend.home import render_home
from frontend.prediction import render_prediction
from frontend.recommendation import render_recommendation
from frontend.theme import inject_global_css


st.set_page_config(
    page_title="CVD Predictor",
    page_icon="🫀",
    layout="wide",
    initial_sidebar_state="expanded",
)

init_db()

if "theme_mode" not in st.session_state:
    st.session_state.theme_mode = "Light"
if "page" not in st.session_state:
    st.session_state.page = "Home"

inject_global_css(st.session_state.theme_mode)

if not login_panel():
    st.stop()

st.sidebar.caption(f"Signed in as: {st.session_state.get('user_role', 'doctor').title()}")
st.session_state.theme_mode = st.sidebar.toggle("Dark Mode", value=st.session_state.theme_mode == "Dark")
st.session_state.theme_mode = "Dark" if st.session_state.theme_mode else "Light"

pages = [
    "Home",
    "Start Prediction",
    "Patient History",
    "Reports",
    "About System",
    "Doctor Recommendations",
    "Contact/Support",
]

selected_page = st.sidebar.radio(
    "Navigation",
    pages,
    index=pages.index(st.session_state.page) if st.session_state.page in pages else 0,
)
st.session_state.page = selected_page

language = st.sidebar.selectbox("Language", ["English", "French", "Hausa", "Yoruba", "Igbo"])
if language != "English":
    st.sidebar.info("Interface translation hooks are prepared; clinical text remains English for safety in this prototype.")

if st.sidebar.button("Sign Out", width="stretch"):
    st.session_state.authenticated = False
    st.session_state.user_role = None
    st.session_state.page = "Home"
    st.rerun()

if selected_page == "Home":
    render_home()
elif selected_page == "Start Prediction":
    render_prediction()
elif selected_page == "Patient History":
    render_dashboard()
elif selected_page == "Reports":
    render_reports()
elif selected_page == "About System":
    render_about()
elif selected_page == "Doctor Recommendations":
    render_recommendation()
elif selected_page == "Contact/Support":
    render_contact()
