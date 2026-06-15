from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path
from typing import Any


BASE_DIR = Path(__file__).resolve().parents[1]
REPORTS_DIR = BASE_DIR / "reports"
ASSETS_DIR = BASE_DIR / "assets"


def _safe_filename(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9_-]", "_", value.strip())
    return cleaned[:60] or "patient"


def create_pdf_report(
    payload: dict[str, Any],
    prediction: dict[str, Any],
    recommendations: dict[str, list[str]],
    explanations: list[dict[str, Any]] | None = None,
) -> Path:
    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
        from reportlab.lib.units import inch
        from reportlab.platypus import (
            Image,
            KeepTogether,
            Paragraph,
            SimpleDocTemplate,
            Spacer,
            Table,
            TableStyle,
        )
    except ImportError as exc:
        raise RuntimeError("Install reportlab to enable PDF report generation.") from exc

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    admission = _safe_filename(payload.get("admission_number", "CVD"))
    output_path = REPORTS_DIR / f"CVD_Report_{admission}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"

    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        rightMargin=0.45 * inch,
        leftMargin=0.45 * inch,
        topMargin=0.45 * inch,
        bottomMargin=0.45 * inch,
    )
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "CVDTitle",
        parent=styles["Title"],
        textColor=colors.HexColor("#b91c1c"),
        fontSize=19,
        leading=23,
        spaceAfter=10,
    )
    section_style = ParagraphStyle(
        "CVDSection",
        parent=styles["Heading2"],
        textColor=colors.HexColor("#0f766e"),
        fontSize=12,
        leading=15,
        spaceBefore=8,
        spaceAfter=6,
    )
    body_style = ParagraphStyle("CVDBody", parent=styles["BodyText"], fontSize=9.5, leading=12)
    footer_style = ParagraphStyle(
        "CVDFooter",
        parent=styles["BodyText"],
        alignment=1,
        textColor=colors.HexColor("#64748b"),
        fontSize=8,
    )

    story = []
    logo_path = ASSETS_DIR / "medical_logo.png"
    if logo_path.exists():
        story.append(Image(str(logo_path), width=0.85 * inch, height=0.85 * inch))
    story.append(Paragraph("CVD Predictor - Heart Disease Medical Report", title_style))
    story.append(Paragraph(f"Generated: {datetime.now().strftime('%d %B %Y, %I:%M %p')}", body_style))
    story.append(Spacer(1, 8))

    def section_table(title: str, rows: list[list[Any]]) -> KeepTogether:
        table = Table(rows, colWidths=[1.9 * inch, 4.7 * inch])
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
                    ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#dbe4ea")),
                    ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#e2e8f0")),
                    ("TEXTCOLOR", (0, 0), (0, -1), colors.HexColor("#0f172a")),
                    ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 8.5),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 8),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                    ("TOPPADDING", (0, 0), (-1, -1), 6),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ]
            )
        )
        return KeepTogether([Paragraph(title, section_style), table])

    patient_rows = [
        ["Patient Name", payload.get("patient_name", "")],
        ["Admission Number", payload.get("admission_number", "")],
        ["Age", payload.get("Age", "")],
        ["Gender", payload.get("Sex", "")],
        ["State", payload.get("state", "")],
        ["Blood Group/Type", payload.get("blood_group", "")],
        ["BMI", payload.get("bmi", "Not calculated")],
    ]
    story.append(section_table("Patient Information", patient_rows))

    medical_keys = [
        "ChestPainType",
        "RestingBP",
        "Cholesterol",
        "FastingBS",
        "RestingECG",
        "MaxHR",
        "ExerciseAngina",
        "Oldpeak",
        "ST_Slope",
        "smoking_status",
        "alcohol_intake",
        "physical_activity",
    ]
    story.append(section_table("Medical Data", [[key, payload.get(key, "")] for key in medical_keys]))

    result_rows = [
        ["Predicted Outcome", prediction["predicted_label"]],
        ["Risk Level", prediction["risk_category"]],
        ["Probability", f"{prediction['probability_percent']}%"],
        ["Confidence Score", f"{prediction['confidence_percent']}%"],
        ["Model Used", prediction["model_name"]],
    ]
    story.append(section_table("Prediction Result", result_rows))

    recommendation_lines = []
    for group, items in recommendations.items():
        recommendation_lines.append(Paragraph(f"<b>{group.replace('_', ' ').title()}</b>", body_style))
        for item in items:
            recommendation_lines.append(Paragraph(f"- {item}", body_style))
    story.append(Paragraph("Recommendations", section_style))
    story.extend(recommendation_lines)

    if explanations:
        story.append(Paragraph("Explainable AI Summary", section_style))
        for item in explanations[:5]:
            story.append(
                Paragraph(
                    f"- {item['Feature']}: {item['Direction']} ({item['Strength']:.3f})",
                    body_style,
                )
            )

    story.append(Spacer(1, 14))
    story.append(Paragraph("Generated by CVD Predictor Intelligent Diagnostic System", footer_style))
    story.append(Paragraph("This report is decision support only and does not replace clinical diagnosis.", footer_style))

    def decorate(canvas, document):
        canvas.saveState()
        width, height = A4
        canvas.setFillColor(colors.HexColor("#fee2e2"))
        canvas.setFont("Helvetica-Bold", 58)
        canvas.setFillAlpha(0.08)
        canvas.translate(width / 2, height / 2)
        canvas.rotate(34)
        canvas.drawCentredString(0, 0, "CVD PREDICTOR")
        canvas.restoreState()

        canvas.saveState()
        canvas.setStrokeColor(colors.HexColor("#ef4444"))
        canvas.setLineWidth(1)
        y = height - 1.2 * inch
        points = [0.5, 0.7, 0.9, 1.0, 1.08, 1.18, 1.28, 1.5, 1.72, 1.94, 2.1]
        for idx in range(len(points) - 1):
            canvas.line(points[idx] * inch, y, points[idx + 1] * inch, y + ((idx % 3) - 1) * 8)
        canvas.restoreState()

    doc.build(story, onFirstPage=decorate, onLaterPages=decorate)
    return output_path
