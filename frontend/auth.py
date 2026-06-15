from __future__ import annotations

import streamlit as st

from utils.security import create_user, validate_registration, verify_password


def login_panel() -> bool:
    if st.session_state.get("authenticated"):
        return True

    login_slot = st.empty()
    with login_slot.container():
        st.markdown(
            """
            <div class="hero">
                <div>
                    <h1>CVD Predictor – Heart Disease Prediction System</h1>
                    <p>Secure clinical access for cardiovascular risk screening, reporting, and patient-history analytics.</p>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.write("")
        left, middle, right = st.columns([1, 1.1, 1])
        with middle:
            st.markdown(
                """
                <div class="login-card">
                    <h2 class="login-title">Doctor Login</h2>
                    <p class="login-copy">Secure access for clinical cardiovascular risk assessment and report generation.</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

            sign_in_tab, register_tab = st.tabs(["Sign In", "Register"])

            with sign_in_tab:
                username = st.text_input("Username", placeholder="Enter your username", key="login_username")
                password = st.text_input("Password", type="password", key="login_password")
                submitted = st.button("Sign In", width="stretch")
                if submitted:
                    if verify_password(username, password):
                        st.session_state.authenticated = True
                        st.session_state.user_role = username.strip().lower()
                        login_slot.empty()
                        return True
                    st.error("Invalid username or password.")

            with register_tab:
                full_name = st.text_input("Full Name", placeholder="Enter clinician name", key="register_full_name")
                new_username = st.text_input("Create Username", placeholder="e.g. dr_amina", key="register_username")
                role = st.selectbox("Role", ["doctor", "clinician", "admin"], format_func=str.title)
                new_password = st.text_input("Create Password", type="password", key="register_password")
                confirm_password = st.text_input("Confirm Password", type="password", key="register_confirm_password")
                register_submitted = st.button("Create Account", width="stretch")
                if register_submitted:
                    errors = validate_registration(full_name, new_username, new_password, confirm_password)
                    if errors:
                        for error in errors:
                            st.error(error)
                    else:
                        created, message = create_user(full_name, new_username, new_password, role)
                        if created:
                            st.success(message)
                        else:
                            st.error(message)
    return False
