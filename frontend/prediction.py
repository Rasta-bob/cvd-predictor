from __future__ import annotations

from html import escape
from pathlib import Path

import pandas as pd
import streamlit as st

from backend.pdf_generator import create_pdf_report
from backend.predictor import explain_prediction, load_metadata, predict_heart_disease
from backend.preprocess import (
    BLOOD_GROUP_OPTIONS,
    MODEL_FEATURE_OPTIONS,
    STATE_OPTIONS,
    clean_payload_for_storage,
    generate_admission_number,
    validate_patient_payload,
)
from backend.recommendation_engine import generate_recommendations
from backend.storage import save_prediction


RISK_TEXT_COLORS = {
    "Low Risk": "#86EFAC",
    "Medium Risk": "#FCD34D",
    "High Risk": "#FCA5A5",
    "Critical Risk": "#EF4444",
}


def _risk_text_color(risk_category: str) -> str:
    return RISK_TEXT_COLORS.get(risk_category, "#FFFFFF")


def _metric_card(title: str, value: str, note: str, value_class: str, extra_style: str = "") -> None:
    st.markdown(
        f"""
        <div class="metric-card" style="{extra_style}">
            <div class="metric-label">{escape(title)}</div>
            <div class="metric-value {value_class}">{escape(value)}</div>
            <div class="metric-note">{escape(note)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _recommendation_card(title: str, items: list[str], accent: str) -> str:
    list_items = "".join(f"<li>{escape(item)}</li>" for item in items)
    return (
        f'<div class="recommendation-card" style="--card-accent:{accent}">'
        f"<h3>{escape(title)}</h3>"
        f"<ul>{list_items}</ul>"
        "</div>"
    )


def _factor_rows(items: list[dict], empty_text: str) -> str:
    if not items:
        return f"<p>{escape(empty_text)}</p>"

    rows = []
    for item in items:
        strength = float(item.get("Strength", 0))
        rows.append(
            '<p class="factor-row">'
            "<span>"
            f'<span class="factor-name">{escape(str(item.get("Feature", "Clinical variable")))}</span>'
            f'<span class="factor-direction">{escape(str(item.get("Direction", "Model contribution")))}</span>'
            "</span>"
            f'<span class="factor-strength">{strength:.3f}</span>'
            "</p>"
        )
    return "".join(rows)


def _render_results_explanation(explanations: list[dict]) -> None:
    if not explanations:
        return

    explanation_df = pd.DataFrame(explanations)
    positive = [item for item in explanations if item.get("Direction") == "Increases risk"]
    negative = [item for item in explanations if item.get("Direction") == "Lowers risk"]
    primary = sorted(explanations, key=lambda item: item.get("Strength", 0), reverse=True)[:3]
    positive = sorted(positive, key=lambda item: item.get("Strength", 0), reverse=True)[:5]
    negative = sorted(negative, key=lambda item: item.get("Strength", 0), reverse=True)[:5]

    st.markdown(
        """
        <div class="section-heading">Results Explanation</div>
        <p class="section-subtitle">
            This section summarizes the clinical variables that most influenced the model output for this patient.
            Positive contributors push the prediction toward higher cardiovascular risk, while negative contributors reduce the predicted risk.
        </p>
        """,
        unsafe_allow_html=True,
    )

    explanation_grid = (
        '<div class="explanation-grid">'
        '<div class="explanation-card" style="--card-accent:#67E8F9">'
        "<h3>Primary Risk Factors</h3>"
        f'{_factor_rows(primary, "No dominant risk factor was identified.")}'
        "</div>"
        '<div class="explanation-card" style="--card-accent:#FCA5A5">'
        "<h3>Positive Contributors</h3>"
        f'{_factor_rows(positive, "No strong positive risk contributors were identified.")}'
        "</div>"
        '<div class="explanation-card" style="--card-accent:#86EFAC">'
        "<h3>Negative Contributors</h3>"
        f'{_factor_rows(negative, "No strong protective contributors were identified.")}'
        "</div>"
        "</div>"
    )
    st.markdown(explanation_grid, unsafe_allow_html=True)

    st.markdown(
        """
        <div class="explanation-card" style="--card-accent:#60A5FA">
            <h3>Model Interpretation Notes</h3>
            <ul>
                <li>Values shown are relative contribution strengths for this prediction, not standalone clinical diagnoses.</li>
                <li>Use this explanation to guide clinical review, patient discussion, and follow-up testing.</li>
                <li>Final medical decisions should remain under qualified clinician oversight.</li>
            </ul>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="section-heading">Feature Importance Summary</div>', unsafe_allow_html=True)
    st.dataframe(explanation_df[["Feature", "Direction", "Strength"]], width="stretch", hide_index=True)
    chart_df = explanation_df.set_index("Feature")["Strength"]
    st.bar_chart(chart_df)


def _payload_form() -> dict:
    if "admission_number" not in st.session_state:
        st.session_state.admission_number = generate_admission_number()

    payload: dict = {}

    tab_basic, tab_clinical, tab_lifestyle = st.tabs(["Basic Information", "Clinical Features", "Lifestyle Context"])

    with tab_basic:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            payload["patient_name"] = st.text_input("Patient Name", placeholder="Enter full name")
            payload["admission_number"] = st.text_input("Admission Number", value=st.session_state.admission_number)
            payload["Age"] = st.number_input("Age", min_value=1, max_value=120, value=54)
            payload["Sex"] = st.selectbox("Gender", MODEL_FEATURE_OPTIONS["Sex"], format_func=lambda x: "Male" if x == "M" else "Female")
        with col2:
            payload["state"] = st.selectbox("State", STATE_OPTIONS, index=STATE_OPTIONS.index("Lagos"))
            payload["blood_group"] = st.selectbox("Blood Group/Type", BLOOD_GROUP_OPTIONS)
            payload["weight"] = st.number_input("Weight (kg)", min_value=2.0, max_value=300.0, value=75.0, step=0.5)
            payload["height"] = st.number_input("Height (cm)", min_value=40.0, max_value=250.0, value=170.0, step=0.5)
        st.markdown("</div>", unsafe_allow_html=True)

    with tab_clinical:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        with col1:
            payload["ChestPainType"] = st.selectbox(
                "Chest Pain Type",
                MODEL_FEATURE_OPTIONS["ChestPainType"],
                format_func=lambda value: {
                    "ASY": "Asymptomatic",
                    "ATA": "Atypical Angina",
                    "NAP": "Non-Anginal Pain",
                    "TA": "Typical Angina",
                }[value],
            )
            payload["RestingBP"] = st.number_input("Resting Blood Pressure (mm Hg)", min_value=40, max_value=260, value=130)
            payload["Cholesterol"] = st.number_input("Cholesterol (mg/dL)", min_value=80, max_value=700, value=220)
            fasting_label = st.radio("Fasting Blood Sugar > 120 mg/dL", ["No", "Yes"], horizontal=True)
            payload["FastingBS"] = 1 if fasting_label == "Yes" else 0
        with col2:
            payload["RestingECG"] = st.selectbox("Resting ECG", MODEL_FEATURE_OPTIONS["RestingECG"])
            payload["MaxHR"] = st.number_input("Maximum Heart Rate", min_value=40, max_value=230, value=140)
            angina_label = st.radio("Exercise Induced Angina", ["No", "Yes"], horizontal=True)
            payload["ExerciseAngina"] = "Y" if angina_label == "Yes" else "N"
            payload["Oldpeak"] = st.number_input("ST Depression / Oldpeak", min_value=-3.0, max_value=8.0, value=0.8, step=0.1)
        with col3:
            payload["ST_Slope"] = st.selectbox("ST Slope", MODEL_FEATURE_OPTIONS["ST_Slope"])
            payload["major_vessels"] = st.slider("Number of Major Vessels", 0, 4, 0)
            payload["thalassemia"] = st.selectbox("Thalassemia", ["Normal", "Fixed defect", "Reversible defect", "Unknown"])
        st.caption("The trained best model uses the original training features; additional clinical fields are saved in the report and recommendations.")
        st.markdown("</div>", unsafe_allow_html=True)

    with tab_lifestyle:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        with col1:
            payload["smoking_status"] = st.selectbox("Smoking Status", ["Never smoked", "Former smoker", "Occasional smoker", "Current smoker"])
        with col2:
            payload["alcohol_intake"] = st.selectbox("Alcohol Intake", ["None", "Low", "Moderate", "High"])
        with col3:
            payload["physical_activity"] = st.selectbox("Physical Activity", ["Sedentary", "Low", "Moderate", "High"])
        st.markdown("</div>", unsafe_allow_html=True)

    return payload


def _render_result(payload: dict, prediction: dict, recommendations: dict, explanations: list[dict]) -> None:
    risk_color = _risk_text_color(prediction["risk_category"])
    st.markdown(
        f"""
        <div class="result-card" style="--accent:{risk_color}">
            <div class="metric-label">Prediction Result</div>
            <h2 style="color:{risk_color}">{escape(prediction['risk_category'])}</h2>
            <p>{escape(prediction['predicted_label'])} using {escape(prediction['model_name'])}.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.write("")
    col1, col2, col3 = st.columns(3)
    with col1:
        _metric_card(
            "Risk Probability",
            f"{prediction['probability_percent']}%",
            "Estimated probability of heart disease risk.",
            "risk-probability",
        )
    with col2:
        _metric_card(
            "Confidence Score",
            f"{prediction['confidence_percent']}%",
            "Model certainty for the displayed prediction.",
            "confidence-score",
        )
    with col3:
        _metric_card(
            "Risk Category",
            prediction["risk_category"],
            "Clinical triage category based on risk probability.",
            "risk-category-value",
            f"--risk-color:{risk_color}",
        )
    st.progress(prediction["probability"])

    if prediction["risk_category"] == "High Risk":
        st.error("Emergency alert: high cardiovascular risk detected. Recommend prompt clinical review.")
    elif prediction["risk_category"] == "Medium Risk":
        st.warning("Moderate cardiovascular risk detected. Schedule clinician follow-up and monitor symptoms.")
    else:
        st.success("Low predicted risk. Continue preventive screening and heart-healthy habits.")

    st.markdown(
        """
        <div class="section-heading">Medical Recommendations</div>
        <p class="section-subtitle">Actionable care guidance generated from the patient's clinical profile and prediction result.</p>
        """,
        unsafe_allow_html=True,
    )
    r1, r2, r3 = st.columns(3)
    for column, title, key, accent in [
        (r1, "Lifestyle Recommendations", "lifestyle", "#2DD4BF"),
        (r2, "Medical Follow-up", "medical", "#60A5FA"),
        (r3, "Alerts and Safety Advice", "emergency", "#FCA5A5"),
    ]:
        with column:
            st.markdown(_recommendation_card(title, recommendations[key], accent), unsafe_allow_html=True)

    _render_results_explanation(explanations)

    try:
        report_path = create_pdf_report(payload, prediction, recommendations, explanations)
        with Path(report_path).open("rb") as file:
            st.download_button(
                "Download PDF Medical Report",
                data=file,
                file_name=Path(report_path).name,
                mime="application/pdf",
                width="stretch",
            )
    except RuntimeError as exc:
        st.info(str(exc))


def render_prediction() -> None:
    metadata = load_metadata()
    st.title("Start Prediction")
    st.caption(f"Active model: {metadata.get('best_model_name', 'Saved best model')}")

    payload = _payload_form()

    st.write("")
    if st.button("Start Prediction", width="stretch"):
        payload = clean_payload_for_storage(payload)
        errors = validate_patient_payload(payload)
        if errors:
            for error in errors:
                st.error(error)
            return

        prediction = predict_heart_disease(payload)
        recommendations = generate_recommendations(payload, prediction)
        explanations = explain_prediction(payload)
        save_prediction(payload, prediction)

        st.session_state.last_prediction = {
            "payload": payload,
            "prediction": prediction,
            "recommendations": recommendations,
            "explanations": explanations,
        }
        _render_result(payload, prediction, recommendations, explanations)
    elif st.session_state.get("last_prediction"):
        cached = st.session_state.last_prediction
        _render_result(
            cached["payload"],
            cached["prediction"],
            cached["recommendations"],
            cached["explanations"],
        )
