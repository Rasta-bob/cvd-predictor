from __future__ import annotations

import re
from datetime import datetime
from typing import Any

import numpy as np
import pandas as pd


TRAINING_FEATURES = [
    "Age",
    "Sex",
    "ChestPainType",
    "RestingBP",
    "Cholesterol",
    "FastingBS",
    "RestingECG",
    "MaxHR",
    "ExerciseAngina",
    "Oldpeak",
    "ST_Slope",
]

MODEL_FEATURE_OPTIONS = {
    "Sex": ["M", "F"],
    "ChestPainType": ["ASY", "ATA", "NAP", "TA"],
    "RestingECG": ["Normal", "ST", "LVH"],
    "ExerciseAngina": ["N", "Y"],
    "ST_Slope": ["Up", "Flat", "Down"],
}

STATE_OPTIONS = [
    "Abia",
    "Adamawa",
    "Akwa Ibom",
    "Anambra",
    "Bauchi",
    "Bayelsa",
    "Benue",
    "Borno",
    "Cross River",
    "Delta",
    "Ebonyi",
    "Edo",
    "Ekiti",
    "Enugu",
    "FCT",
    "Gombe",
    "Imo",
    "Jigawa",
    "Kaduna",
    "Kano",
    "Katsina",
    "Kebbi",
    "Kogi",
    "Kwara",
    "Lagos",
    "Nasarawa",
    "Niger",
    "Ogun",
    "Ondo",
    "Osun",
    "Oyo",
    "Plateau",
    "Rivers",
    "Sokoto",
    "Taraba",
    "Yobe",
    "Zamfara",
]

BLOOD_GROUP_OPTIONS = ["AA", "AS", "SS", "AC", "SC", "O+", "O-", "A+", "A-", "B+", "B-", "AB+", "AB-"]


def generate_admission_number() -> str:
    timestamp = datetime.now().strftime("%H%M%S")
    return f"CVD-{timestamp}"


def sanitize_text(value: Any, max_length: int = 80) -> str:
    text = str(value or "").strip()
    text = re.sub(r"[^A-Za-z0-9 .,'_/()#-]", "", text)
    return text[:max_length]


def bmi(weight_kg: float, height_cm: float) -> float | None:
    if not weight_kg or not height_cm:
        return None
    height_m = height_cm / 100
    if height_m <= 0:
        return None
    return round(weight_kg / (height_m**2), 1)


def risk_category(probability: float) -> tuple[str, str]:
    if probability < 0.35:
        return "Low Risk", "#0f9f6e"
    if probability < 0.65:
        return "Medium Risk", "#d97706"
    return "High Risk", "#dc2626"


def validate_patient_payload(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    if not sanitize_text(payload.get("patient_name")):
        errors.append("Patient name is required.")
    if not sanitize_text(payload.get("admission_number")):
        errors.append("Admission number is required.")

    ranges = {
        "Age": (1, 120),
        "RestingBP": (40, 260),
        "Cholesterol": (80, 700),
        "MaxHR": (40, 230),
        "Oldpeak": (-3.0, 8.0),
        "weight": (2, 300),
        "height": (40, 250),
    }
    for key, (low, high) in ranges.items():
        value = payload.get(key)
        if value is None:
            errors.append(f"{key} is required.")
            continue
        try:
            numeric_value = float(value)
        except (TypeError, ValueError):
            errors.append(f"{key} must be numeric.")
            continue
        if numeric_value < low or numeric_value > high:
            errors.append(f"{key} must be between {low} and {high}.")

    for key, values in MODEL_FEATURE_OPTIONS.items():
        if payload.get(key) not in values:
            errors.append(f"{key} must be one of: {', '.join(values)}.")

    if payload.get("FastingBS") not in [0, 1]:
        errors.append("Fasting blood sugar status must be selected.")

    return errors


def build_model_input(payload: dict[str, Any]) -> pd.DataFrame:
    row = {
        "Age": int(payload["Age"]),
        "Sex": payload["Sex"],
        "ChestPainType": payload["ChestPainType"],
        "RestingBP": float(payload["RestingBP"]),
        "Cholesterol": float(payload["Cholesterol"]),
        "FastingBS": int(payload["FastingBS"]),
        "RestingECG": payload["RestingECG"],
        "MaxHR": float(payload["MaxHR"]),
        "ExerciseAngina": payload["ExerciseAngina"],
        "Oldpeak": float(payload["Oldpeak"]),
        "ST_Slope": payload["ST_Slope"],
    }
    return pd.DataFrame([row], columns=TRAINING_FEATURES)


def clean_payload_for_storage(payload: dict[str, Any]) -> dict[str, Any]:
    cleaned = payload.copy()
    for key in ["patient_name", "admission_number", "state", "blood_group"]:
        cleaned[key] = sanitize_text(cleaned.get(key))
    cleaned["bmi"] = bmi(float(cleaned.get("weight", 0)), float(cleaned.get("height", 0)))
    return cleaned


def safe_probability(value: float) -> float:
    return float(np.clip(value, 0.0, 1.0))
