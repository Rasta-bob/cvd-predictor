from __future__ import annotations

import json
import pickle
from functools import lru_cache
from pathlib import Path
from typing import Any

import numpy as np

from .preprocess import build_model_input, risk_category, safe_probability


BASE_DIR = Path(__file__).resolve().parents[1]
MODEL_DIR = BASE_DIR / "models"
DEFAULT_MODEL_PATHS = [
    MODEL_DIR / "best_model.pkl",
    MODEL_DIR / "best_heart_disease_model.joblib",
    BASE_DIR.parent / "best_heart_disease_model.joblib",
]
METADATA_PATH = MODEL_DIR / "best_model_metadata.json"


@lru_cache(maxsize=1)
def load_model(model_path: str | None = None):
    candidate_paths = [Path(model_path)] if model_path else DEFAULT_MODEL_PATHS
    existing_path = next((path for path in candidate_paths if path.exists()), None)
    if existing_path is None:
        raise FileNotFoundError("No saved model artifact was found in the models folder.")

    try:
        import joblib

        return joblib.load(existing_path)
    except Exception:
        with existing_path.open("rb") as model_file:
            return pickle.load(model_file)


@lru_cache(maxsize=1)
def load_metadata() -> dict[str, Any]:
    if METADATA_PATH.exists():
        return json.loads(METADATA_PATH.read_text(encoding="utf-8"))
    return {
        "best_model_name": "Saved best model",
        "target": "HeartDisease",
        "selection_rule": "Best selected model from training workflow",
    }


def _positive_probability(model, model_input) -> float:
    if hasattr(model, "predict_proba"):
        probability = model.predict_proba(model_input)[0][1]
        return safe_probability(probability)

    decision = model.decision_function(model_input)[0]
    probability = 1 / (1 + np.exp(-decision))
    return safe_probability(probability)


def predict_heart_disease(payload: dict[str, Any]) -> dict[str, Any]:
    model = load_model()
    model_input = build_model_input(payload)

    probability = _positive_probability(model, model_input)
    prediction = int(probability >= 0.5)
    confidence = max(probability, 1 - probability)
    category, color = risk_category(probability)

    return {
        "prediction": prediction,
        "predicted_label": "Heart Disease Risk Detected" if prediction else "No Significant Heart Disease Risk Detected",
        "probability": probability,
        "probability_percent": round(probability * 100, 2),
        "confidence": confidence,
        "confidence_percent": round(confidence * 100, 2),
        "risk_category": category,
        "risk_color": color,
        "model_name": load_metadata().get("best_model_name", "Saved best model"),
        "model_input": model_input,
    }


def get_feature_names(fitted_pipeline) -> list[str]:
    if not hasattr(fitted_pipeline, "named_steps"):
        return []

    preprocessor = fitted_pipeline.named_steps.get("preprocessor")
    if preprocessor is None:
        return []

    feature_names: list[str] = []
    for transformer_name, transformer, columns in preprocessor.transformers_:
        if transformer_name == "remainder" or transformer == "drop":
            continue
        if transformer_name == "num":
            feature_names.extend(list(columns))
        elif transformer_name == "cat":
            encoder = transformer.named_steps.get("onehot") if hasattr(transformer, "named_steps") else None
            if encoder is not None and hasattr(encoder, "get_feature_names_out"):
                feature_names.extend(encoder.get_feature_names_out(columns).tolist())
            else:
                feature_names.extend(list(columns))
    return feature_names


def explain_prediction(payload: dict[str, Any], limit: int = 8) -> list[dict[str, Any]]:
    model = load_model()
    if not hasattr(model, "named_steps"):
        return []

    model_input = build_model_input(payload)
    preprocessor = model.named_steps.get("preprocessor")
    estimator = model.named_steps.get("model")
    if preprocessor is None or estimator is None:
        return []

    transformed = preprocessor.transform(model_input)
    if hasattr(transformed, "toarray"):
        transformed = transformed.toarray()
    transformed = np.asarray(transformed)[0]
    feature_names = get_feature_names(model)

    if hasattr(estimator, "coef_"):
        weights = estimator.coef_[0]
        contributions = transformed * weights
        rows = [
            {
                "Feature": feature_names[i] if i < len(feature_names) else f"feature_{i}",
                "Contribution": float(contributions[i]),
                "Direction": "Increases risk" if contributions[i] > 0 else "Lowers risk",
                "Strength": float(abs(contributions[i])),
            }
            for i in range(len(contributions))
        ]
    elif hasattr(estimator, "feature_importances_"):
        importances = estimator.feature_importances_
        rows = [
            {
                "Feature": feature_names[i] if i < len(feature_names) else f"feature_{i}",
                "Contribution": float(importances[i]),
                "Direction": "Important predictor",
                "Strength": float(importances[i]),
            }
            for i in range(len(importances))
        ]
    else:
        return []

    return sorted(rows, key=lambda item: item["Strength"], reverse=True)[:limit]
