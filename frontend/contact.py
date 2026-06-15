from __future__ import annotations

import streamlit as st


def render_contact() -> None:
    st.title("Contact/Support")
    st.markdown(
        """
        <div class="glass-card">
            <h3>Clinical Support Desk</h3>
            <p class="small-muted">For deployment, connect this section to the hospital helpdesk, incident-response workflow, and model-governance contacts.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.write("")
    col1, col2 = st.columns(2)
    with col1:
        st.text_input("Doctor Name")
        st.text_input("Hospital Email")
    with col2:
        st.selectbox("Request Type", ["Clinical question", "Technical support", "Model governance", "Report issue"])
        st.text_area("Message")
    if st.button("Send Support Request"):
        st.success("Support request captured for the demo workflow.")
