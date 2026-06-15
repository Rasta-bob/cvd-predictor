from __future__ import annotations

import streamlit as st


def render_recommendation() -> None:
    st.title("Doctor Recommendations")
    st.markdown(
        """
        <div class="glass-card">
            <h3>Clinical Follow-up Framework</h3>
            <p class="small-muted">Recommendations are generated from risk probability, key cardiovascular measurements, and lifestyle context.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.write("")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Lifestyle Care")
        st.write("- Encourage Mediterranean-style or DASH-style nutrition.")
        st.write("- Support progressive exercise plans after medical clearance.")
        st.write("- Address smoking, alcohol intake, sleep, and stress patterns.")
    with col2:
        st.subheader("Medical Care")
        st.write("- Review ECG and lipid profile when risk is moderate or high.")
        st.write("- Monitor blood pressure and glycemic status.")
        st.write("- Refer high-risk patients to cardiology promptly.")

    if st.session_state.get("last_prediction"):
        st.info("A recent prediction is available. Open Start Prediction to download the full report.")
