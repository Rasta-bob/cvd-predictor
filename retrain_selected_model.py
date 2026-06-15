from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from joblib import dump
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder


BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR.parent / "heart.csv"
MODELS_DIR = BASE_DIR / "models"


def main() -> None:
    df = pd.read_csv(DATA_PATH)
    target_col = "HeartDisease"
    df_model = df.copy()
    for col in ["RestingBP", "Cholesterol"]:
        df_model[col] = df_model[col].replace(0, np.nan)

    X = df_model.drop(columns=[target_col])
    y = df_model[target_col]

    numeric_features = X.select_dtypes(include=["int64", "float64"]).columns.tolist()
    categorical_features = X.select_dtypes(include=["object", "category", "bool"]).columns.tolist()

    X_train, _, y_train, _ = train_test_split(
        X,
        y,
        test_size=0.30,
        random_state=42,
        stratify=y,
    )

    try:
        encoder = OneHotEncoder(handle_unknown="ignore", sparse_output=False)
    except TypeError:
        encoder = OneHotEncoder(handle_unknown="ignore", sparse=False)

    preprocessor = ColumnTransformer(
        transformers=[
            (
                "num",
                Pipeline(steps=[("imputer", SimpleImputer(strategy="median"))]),
                numeric_features,
            ),
            (
                "cat",
                Pipeline(
                    steps=[
                        ("imputer", SimpleImputer(strategy="most_frequent")),
                        ("onehot", encoder),
                    ]
                ),
                categorical_features,
            ),
        ]
    )

    model = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            (
                "model",
                RandomForestClassifier(
                    n_estimators=400,
                    max_depth=6,
                    min_samples_leaf=2,
                    min_samples_split=2,
                    random_state=42,
                    class_weight="balanced",
                ),
            ),
        ]
    )
    model.fit(X_train, y_train)

    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    dump(model, MODELS_DIR / "best_model.pkl")

    metadata = {
        "best_model_name": "Random Forest",
        "best_params": {
            "model__max_depth": 6,
            "model__min_samples_leaf": 2,
            "model__min_samples_split": 2,
            "model__n_estimators": 400,
        },
        "target": target_col,
        "numeric_features": numeric_features,
        "categorical_features": categorical_features,
        "invalid_zero_values_imputed": ["RestingBP", "Cholesterol"],
        "selection_rule": "Highest test ROC-AUC, then F1-score and recall",
        "train_test_split": "70% train / 30% test",
        "serialization_note": "Regenerated with the current scikit-learn runtime for Streamlit app compatibility.",
    }
    (MODELS_DIR / "best_model_metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    print("Regenerated models/best_model.pkl")


if __name__ == "__main__":
    main()
