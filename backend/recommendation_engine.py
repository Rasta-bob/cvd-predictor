from __future__ import annotations

from typing import Any


def generate_recommendations(payload: dict[str, Any], prediction: dict[str, Any]) -> dict[str, list[str]]:
    probability = prediction["probability"]
    risk_category = prediction["risk_category"]

    lifestyle = [
        "Adopt a heart-healthy diet rich in vegetables, fruits, legumes, whole grains, and lean protein.",
        "Aim for at least 150 minutes of moderate aerobic activity weekly if medically cleared.",
        "Maintain consistent sleep routines and target 7 to 9 hours of quality sleep per night.",
        "Practice stress reduction through breathing exercises, counselling, mindfulness, or clinician-guided therapy.",
    ]

    medical = [
        "Review this result with a qualified clinician; the model is a decision-support tool, not a diagnosis.",
        "Monitor blood pressure regularly and document readings for follow-up visits.",
        "Schedule lipid profile review and cholesterol management if values remain elevated.",
    ]

    alerts = []

    if payload.get("smoking_status") in {"Current smoker", "Occasional smoker"}:
        lifestyle.append("Begin a smoking cessation plan and discuss nicotine replacement or medical support with a clinician.")

    if payload.get("alcohol_intake") in {"High", "Moderate"}:
        lifestyle.append("Reduce alcohol intake and follow clinician-approved limits.")

    if payload.get("physical_activity") in {"Sedentary", "Low"}:
        lifestyle.append("Start with low-impact walking or supervised exercise and gradually increase intensity.")

    if float(payload.get("RestingBP", 0)) >= 140:
        medical.append("Elevated resting blood pressure was entered; consider hypertension assessment and management.")

    if float(payload.get("Cholesterol", 0)) >= 240:
        medical.append("High cholesterol was entered; consider lipid-lowering counselling and repeat laboratory testing.")

    if payload.get("ExerciseAngina") == "Y":
        medical.append("Exercise-induced angina was reported; cardiology review and ECG/stress testing may be appropriate.")

    if probability >= 0.65:
        alerts.extend(
            [
                "High-risk prediction: recommend prompt cardiology consultation.",
                "If the patient has chest pain, shortness of breath, fainting, or severe sweating, seek emergency care immediately.",
            ]
        )
    elif probability >= 0.35:
        alerts.append("Moderate-risk prediction: schedule non-urgent clinician review and monitor symptoms closely.")
    else:
        alerts.append("Low-risk prediction: continue preventive screening and healthy lifestyle habits.")

    return {
        "risk_category": [f"Overall risk category: {risk_category}"],
        "lifestyle": lifestyle,
        "medical": medical,
        "emergency": alerts,
    }
