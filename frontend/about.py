from __future__ import annotations

import pandas as pd
import streamlit as st

from backend.predictor import load_metadata


def render_about() -> None:
    metadata = load_metadata()
    st.title("About System")
    st.markdown(
        """
        <div class="glass-card">
            <h3>CVD Predictor – Heart Disease Prediction System</h3>
            <p class="small-muted">A Streamlit-based medical AI prototype for cardiovascular risk screening, patient reporting, and model transparency.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.write("")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Model")
        st.json(metadata)
    with col2:
        st.subheader("Training Comparison")
        results_path = "models/model_comparison_results.csv"
        try:
            results = pd.read_csv(results_path)
            st.dataframe(results, width="stretch", hide_index=True)
        except FileNotFoundError:
            st.info("Model comparison table was not found.")

    st.warning(
        "Clinical safety note: the model was trained on a limited dataset and requires external validation, calibration, governance review, and clinician oversight before real-world deployment."
    )
