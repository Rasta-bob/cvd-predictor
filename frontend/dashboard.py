from __future__ import annotations

import pandas as pd
import streamlit as st

from backend.storage import dashboard_stats, fetch_history


def render_dashboard() -> None:
    st.title("Patient History")
    stats = dashboard_stats()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Patients", stats["total"])
    c2.metric("High Risk", stats["high_risk"])
    c3.metric("Medium Risk", stats["medium_risk"])
    c4.metric("Average Risk", f"{stats['avg_probability'] * 100:.1f}%")

    history = fetch_history()
    if not history:
        st.info("No prediction history has been recorded yet.")
        return

    history_df = pd.DataFrame(history)
    history_df["probability_percent"] = (history_df["probability"] * 100).round(2)
    st.dataframe(history_df, width="stretch", hide_index=True)

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Risk Distribution")
        st.bar_chart(history_df["risk_category"].value_counts())
    with col2:
        st.subheader("Recent Probability Trend")
        trend = history_df.sort_values("created_at").set_index("created_at")["probability_percent"]
        st.line_chart(trend)


def render_reports() -> None:
    from pathlib import Path

    reports_dir = Path(__file__).resolve().parents[1] / "reports"
    reports_dir.mkdir(exist_ok=True)
    st.title("Reports")
    report_files = sorted(reports_dir.glob("*.pdf"), key=lambda path: path.stat().st_mtime, reverse=True)
    if not report_files:
        st.info("No PDF reports have been generated yet.")
        return

    for report in report_files:
        with report.open("rb") as file:
            st.download_button(
                label=f"Download {report.name}",
                data=file,
                file_name=report.name,
                mime="application/pdf",
                width="stretch",
            )
