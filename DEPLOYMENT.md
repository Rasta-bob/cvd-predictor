# Deployment Guide

## Streamlit Cloud

1. Push `CVD_Predictor/` to GitHub.
2. Create a Streamlit Cloud app.
3. Set the main file path to `CVD_Predictor/app.py`.
4. Add secrets or environment variables for:
   - `CVD_DOCTOR_PASSWORD`
   - `CVD_ADMIN_PASSWORD`
5. Deploy.

## Render

Use a Python web service.

Build command:

```bash
pip install -r requirements.txt
```

Start command:

```bash
streamlit run app.py --server.port $PORT --server.address 0.0.0.0
```

## Railway

1. Create a new Railway project from GitHub.
2. Set the root directory to `CVD_Predictor`.
3. Add environment variables for doctor/admin passwords.
4. Use the same Streamlit start command as Render.

## Hugging Face Spaces

1. Create a new Space using the Streamlit SDK.
2. Upload the contents of `CVD_Predictor/`.
3. Ensure `requirements.txt`, `app.py`, `models/best_model.pkl`, and `assets/` are included.
4. Add credentials as repository secrets when available.

## Production Notes

- Replace demo credentials before deployment.
- Use encrypted storage for patient identifiers in production.
- Add HTTPS, audit logging, access controls, and retention policies.
- Validate predictions on local patient populations before clinical use.
- Keep model artifacts versioned and document approvals.
