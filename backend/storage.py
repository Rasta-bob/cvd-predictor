from __future__ import annotations

import hashlib
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any


BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "patient_history.db"


def init_db() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL,
                patient_hash TEXT NOT NULL,
                patient_initials TEXT NOT NULL,
                admission_number TEXT NOT NULL,
                age INTEGER,
                state TEXT,
                blood_group TEXT,
                prediction_label TEXT,
                risk_category TEXT,
                probability REAL,
                confidence REAL,
                model_name TEXT
            )
            """
        )
        conn.commit()


def _hash_patient(name: str, admission_number: str) -> str:
    raw = f"{name.strip().lower()}::{admission_number.strip().upper()}".encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _initials(name: str) -> str:
    parts = [part for part in name.strip().split() if part]
    return "".join(part[0].upper() for part in parts[:3]) or "PT"


def save_prediction(payload: dict[str, Any], prediction: dict[str, Any]) -> None:
    init_db()
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            INSERT INTO predictions (
                created_at,
                patient_hash,
                patient_initials,
                admission_number,
                age,
                state,
                blood_group,
                prediction_label,
                risk_category,
                probability,
                confidence,
                model_name
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                datetime.now().isoformat(timespec="seconds"),
                _hash_patient(payload.get("patient_name", ""), payload.get("admission_number", "")),
                _initials(payload.get("patient_name", "")),
                payload.get("admission_number", ""),
                int(payload.get("Age", 0)),
                payload.get("state", ""),
                payload.get("blood_group", ""),
                prediction.get("predicted_label", ""),
                prediction.get("risk_category", ""),
                float(prediction.get("probability", 0)),
                float(prediction.get("confidence", 0)),
                prediction.get("model_name", ""),
            ),
        )
        conn.commit()


def fetch_history(limit: int = 200):
    init_db()
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            """
            SELECT created_at, patient_initials, admission_number, age, state, blood_group,
                   prediction_label, risk_category, probability, confidence, model_name
            FROM predictions
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
    return [dict(row) for row in rows]


def dashboard_stats() -> dict[str, Any]:
    history = fetch_history(limit=10000)
    total = len(history)
    high_risk = sum(1 for row in history if row["risk_category"] == "High Risk")
    medium_risk = sum(1 for row in history if row["risk_category"] == "Medium Risk")
    low_risk = sum(1 for row in history if row["risk_category"] == "Low Risk")
    avg_probability = sum(row["probability"] for row in history) / total if total else 0
    return {
        "total": total,
        "high_risk": high_risk,
        "medium_risk": medium_risk,
        "low_risk": low_risk,
        "avg_probability": avg_probability,
        "history": history,
    }
