# CVD Predictor - Heart Disease Prediction System

Professional Streamlit application for cardiovascular risk prediction using the selected best trained model from the machine-learning workflow.

## What Is Included

- Streamlit medical web interface
- User registration and login
- Real-time heart disease risk prediction
- Recommendation engine
- PDF medical report generation
- SQLite patient history
- Dashboard analytics
- Explainable AI feature contribution view
- Light/dark theme toggle
- Deployment-ready project structure

## Model

The app loads the saved best model from:

```text
models/best_model.pkl
```

The current model artifact is a Random Forest pipeline selected from the 70% training and 30% testing workflow. It includes preprocessing, encoding, imputation, and the trained estimator.

## Run Locally

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

Open:

```text
http://localhost:8501
```

New clinicians can register directly from the login page.

## Project Structure

```text
CVD_Predictor/
|-- app.py
|-- frontend/
|-- backend/
|-- utils/
|-- models/
|-- assets/
|-- reports/
|-- data/
|-- requirements.txt
|-- README.md
|-- DEPLOYMENT.md
|-- Procfile
`-- runtime.txt
```

## Clinical Safety

This application is a clinical decision-support prototype. It is not a diagnostic device and should not be used without clinician oversight, external validation, calibration, privacy review, and hospital governance approval.
