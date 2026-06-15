from __future__ import annotations

import streamlit as st

from .theme import card


def render_home() -> None:
    st.markdown(
        """
        <div class="hero">
            <div>
                <h1>CVD Predictor – Heart Disease Prediction System</h1>
                <p>Hospital-grade cardiovascular risk assessment with real-time prediction, explainable AI, patient history, and professional PDF reporting.</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.write("")
    col1, col2, col3 = st.columns(3)
    with col1:
        card("Real-Time Prediction", "Runs the selected best model using the same features used during training.", "♡")
    with col2:
        card("Clinical Reports", "Produces downloadable patient reports with risk level, confidence, and recommendations.", "✚")
    with col3:
        card("Doctor Dashboard", "Tracks patient history, risk distribution, high-risk alerts, and model outputs.", "⌁")

    st.write("")
    st.warning(
        "Medical disclaimer: this application is a clinical decision-support prototype. It does not replace diagnosis, emergency care, or professional medical judgment."
    )

    cta_col, _ = st.columns([0.35, 0.65])
    with cta_col:
        if st.button("Start Prediction", width="stretch"):
            st.session_state.page = "Start Prediction"
            st.rerun()

    st.markdown('<div class="ecg-line"></div>', unsafe_allow_html=True)
