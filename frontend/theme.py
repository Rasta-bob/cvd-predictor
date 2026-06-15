from __future__ import annotations

import base64
from pathlib import Path

import streamlit as st


BASE_DIR = Path(__file__).resolve().parents[1]
ASSETS_DIR = BASE_DIR / "assets"


def _asset_base64(path: Path) -> str:
    if not path.exists():
        return ""
    return base64.b64encode(path.read_bytes()).decode("utf-8")


def inject_global_css(mode: str = "Light") -> None:
    dark = mode == "Dark"
    text = "#ffffff"
    muted = "#e2e8f0"
    panel = "rgba(10, 24, 38, 0.78)" if dark else "rgba(15, 23, 42, 0.74)"
    panel_strong = "rgba(15, 23, 42, 0.92)" if dark else "rgba(15, 23, 42, 0.86)"
    border = "rgba(226, 232, 240, 0.22)" if dark else "rgba(226, 232, 240, 0.18)"
    bg_image = _asset_base64(ASSETS_DIR / "heart_bg.jpg")
    logo = _asset_base64(ASSETS_DIR / "logo.png")

    bg_css = (
        f"background-image: linear-gradient(120deg, rgba(2, 6, 23, 0.72), rgba(15, 118, 110, 0.35)), url(data:image/jpeg;base64,{bg_image});"
        if bg_image
        else "background: radial-gradient(circle at top left, rgba(239, 68, 68, .25), transparent 32%), linear-gradient(135deg, #07111f, #0f766e);"
    )

    st.markdown(
        f"""
        <style>
        :root {{
            --cvd-red: #dc2626;
            --cvd-teal: #0f766e;
            --cvd-blue: #0369a1;
            --cvd-accent-blue: #60a5fa;
            --cvd-accent-cyan: #67e8f9;
            --cvd-accent-teal: #2dd4bf;
            --cvd-success: #86efac;
            --cvd-warning: #fcd34d;
            --cvd-danger: #fca5a5;
            --cvd-text: {text};
            --cvd-muted: {muted};
            --cvd-panel: {panel};
            --cvd-panel-strong: {panel_strong};
            --cvd-border: {border};
        }}

        .stApp {{
            {bg_css}
            background-attachment: fixed;
            background-size: cover;
            color: var(--cvd-text);
        }}

        .stApp::before {{
            content: "";
            position: fixed;
            inset: 0;
            pointer-events: none;
            opacity: .22;
            background:
                linear-gradient(90deg, transparent 0 7%, rgba(255,255,255,.22) 7.2%, transparent 7.5% 100%),
                repeating-linear-gradient(0deg, transparent 0 28px, rgba(255,255,255,.08) 29px);
            animation: cvdPulse 8s linear infinite;
            z-index: 0;
        }}

        @keyframes cvdPulse {{
            0% {{ transform: translateX(-4%); opacity: .12; }}
            50% {{ opacity: .24; }}
            100% {{ transform: translateX(4%); opacity: .12; }}
        }}

        section[data-testid="stSidebar"] {{
            background: rgba(5, 17, 32, .92);
            border-right: 1px solid rgba(255,255,255,.1);
        }}

        .block-container {{
            position: relative;
            z-index: 1;
            padding-top: 1.2rem;
            max-width: 1280px;
        }}

        h1, h2, h3, h4, p, label, span, div {{
            letter-spacing: 0;
        }}

        h1, h2, h3, h4 {{
            color: #ffffff;
            text-shadow: 0 2px 16px rgba(2, 6, 23, .45);
        }}

        p, label, .stMarkdown, div[data-testid="stCaptionContainer"] {{
            color: var(--cvd-muted);
        }}

        .cvd-brand {{
            display: flex;
            align-items: center;
            gap: .75rem;
            padding: .75rem .25rem 1.1rem;
        }}

        .cvd-brand img {{
            width: 48px;
            height: 48px;
            object-fit: contain;
        }}

        .cvd-brand-title {{
            color: #fff;
            font-weight: 800;
            font-size: 1.02rem;
            line-height: 1.1;
        }}

        .cvd-brand-subtitle {{
            color: #bde7e2;
            font-size: .78rem;
            margin-top: .2rem;
        }}

        .glass-card, .metric-card, .result-card, .login-card, .recommendation-card, .explanation-card {{
            background: var(--cvd-panel);
            border: 1px solid var(--cvd-border);
            border-radius: 8px;
            box-shadow: 0 22px 60px rgba(2, 6, 23, .26);
            backdrop-filter: blur(14px);
            padding: 1.1rem;
            color: #ffffff;
        }}

        .glass-card h3,
        .glass-card p,
        .recommendation-card h3,
        .recommendation-card p,
        .recommendation-card li,
        .explanation-card h3,
        .explanation-card p,
        .explanation-card li,
        .login-card h2,
        .login-card p {{
            color: #ffffff;
        }}

        .login-title {{
            color: #ffffff;
            font-size: 1.55rem;
            font-weight: 850;
            margin: 0 0 .35rem;
            text-shadow: 0 2px 18px rgba(2, 6, 23, .66);
        }}

        .login-copy {{
            color: #e0f7fa;
            line-height: 1.65;
            margin-bottom: .8rem;
        }}

        div[data-testid="stTextInput"] label,
        div[data-testid="stNumberInput"] label,
        div[data-testid="stSelectbox"] label,
        div[data-testid="stRadio"] label,
        div[data-testid="stSlider"] label {{
            color: #f8fafc !important;
            font-weight: 750;
            text-shadow: 0 1px 10px rgba(2, 6, 23, .38);
        }}

        div[data-testid="stTextInput"] input,
        div[data-testid="stNumberInput"] input {{
            color: #ffffff;
            background: rgba(15, 23, 42, .88);
            border: 1px solid rgba(226, 232, 240, .26);
        }}

        div[data-baseweb="select"] > div {{
            color: #ffffff;
            background: rgba(15, 23, 42, .88);
            border-color: rgba(226, 232, 240, .26);
        }}

        .hero {{
            min-height: 360px;
            display: grid;
            align-items: center;
            padding: 2.5rem;
            border-radius: 8px;
            background:
                linear-gradient(120deg, rgba(127, 29, 29, .88), rgba(15, 118, 110, .72)),
                radial-gradient(circle at 78% 28%, rgba(255,255,255,.24), transparent 20%);
            color: #fff;
            overflow: hidden;
            position: relative;
        }}

        .hero::after {{
            content: "✚";
            position: absolute;
            right: 6%;
            top: 10%;
            color: rgba(255,255,255,.12);
            font-size: 10rem;
            line-height: 1;
        }}

        .hero h1 {{
            color: #fff;
            font-size: clamp(2rem, 5vw, 4.4rem);
            line-height: 1.02;
            max-width: 870px;
        }}

        .hero p {{
            color: #e7fbfb;
            max-width: 780px;
            font-size: 1.05rem;
        }}

        .metric-card {{
            min-height: 118px;
        }}

        .metric-label {{
            color: #e2e8f0;
            font-size: .82rem;
            text-transform: uppercase;
            font-weight: 850;
            letter-spacing: .04em;
        }}

        .metric-value {{
            font-size: 2.25rem;
            font-weight: 900;
            color: #ffffff;
            margin-top: .3rem;
            line-height: 1.05;
            text-shadow: 0 2px 18px rgba(2, 6, 23, .55);
        }}

        .metric-note {{
            color: #e2e8f0;
            margin-top: .45rem;
            font-size: .9rem;
            line-height: 1.45;
        }}

        .risk-probability {{
            color: #64ffda;
        }}

        .confidence-score {{
            color: #7dd3fc;
        }}

        .risk-category-value {{
            color: var(--risk-color, #f8fafc);
        }}

        .result-card {{
            border-left: 6px solid var(--accent, #0f766e);
            margin-bottom: 1rem;
        }}

        .result-card h2 {{
            font-size: 2rem;
            font-weight: 900;
            margin: .25rem 0;
        }}

        .result-card p {{
            color: #e0ffff;
            font-size: 1rem;
            line-height: 1.65;
            margin-bottom: 0;
        }}

        .stButton > button, .stDownloadButton > button {{
            border-radius: 8px;
            border: 0;
            background: linear-gradient(135deg, #dc2626, #0f766e);
            color: white;
            font-weight: 800;
            min-height: 2.8rem;
            box-shadow: 0 14px 28px rgba(15, 118, 110, .24);
        }}

        .stButton > button:hover, .stDownloadButton > button:hover {{
            transform: translateY(-1px);
            color: white;
            border: 0;
        }}

        div[data-testid="stMetricValue"] {{
            color: #ffffff;
            font-weight: 900;
        }}

        .small-muted {{
            color: var(--cvd-muted);
            font-size: .88rem;
            line-height: 1.6;
        }}

        .section-heading {{
            color: #ffffff;
            font-weight: 900;
            font-size: 1.55rem;
            margin: 1.35rem 0 .75rem;
            text-shadow: 0 2px 18px rgba(2, 6, 23, .5);
        }}

        .section-subtitle {{
            color: #dbeafe;
            line-height: 1.65;
            margin-top: -.25rem;
            margin-bottom: 1rem;
        }}

        .recommendation-card {{
            min-height: 100%;
            border-top: 4px solid var(--card-accent, #67e8f9);
        }}

        .recommendation-card h3 {{
            font-size: 1.1rem;
            font-weight: 900;
            margin: 0 0 .75rem;
            color: #ffffff;
        }}

        .recommendation-card ul {{
            padding-left: 1.1rem;
            margin: 0;
        }}

        .recommendation-card li {{
            color: #e5e7eb;
            line-height: 1.72;
            margin-bottom: .65rem;
            font-size: .98rem;
        }}

        .explanation-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(230px, 1fr));
            gap: .85rem;
            margin: .8rem 0 1rem;
        }}

        .explanation-card {{
            border-top: 4px solid var(--card-accent, #67e8f9);
        }}

        .explanation-card h3 {{
            color: #ffffff;
            font-size: 1.05rem;
            font-weight: 900;
            margin: 0 0 .55rem;
        }}

        .explanation-card p,
        .explanation-card li {{
            color: #e0ffff;
            font-size: .98rem;
            line-height: 1.68;
        }}

        .factor-row {{
            display: grid;
            grid-template-columns: minmax(0, 1fr) auto;
            gap: .75rem;
            align-items: center;
            padding: .72rem .78rem;
            margin-bottom: .55rem;
            border-radius: 8px;
            background: rgba(15, 23, 42, .66);
            border: 1px solid rgba(226, 232, 240, .14);
        }}

        .factor-name {{
            display: block;
            color: #ffffff;
            font-weight: 850;
            font-size: .96rem;
        }}

        .factor-direction {{
            display: block;
            color: #e2e8f0;
            font-size: .84rem;
            margin-top: .12rem;
        }}

        .factor-strength {{
            color: #67e8f9;
            font-weight: 900;
            white-space: nowrap;
        }}

        .badge {{
            display: inline-flex;
            align-items: center;
            border-radius: 999px;
            padding: .22rem .6rem;
            color: #07111f;
            font-weight: 900;
            font-size: .78rem;
            background: var(--badge-bg, #67e8f9);
        }}

        .streamlit-expanderHeader {{
            color: #ffffff !important;
            font-weight: 850;
        }}

        .ecg-line {{
            height: 58px;
            border-radius: 8px;
            background:
                linear-gradient(90deg, transparent 0 6%, #fca5a5 6.2% 6.8%, transparent 7% 100%),
                repeating-linear-gradient(90deg, rgba(255,255,255,.08) 0 1px, transparent 1px 20px);
            animation: cvdPulse 3.5s ease-in-out infinite;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )

    if logo:
        st.sidebar.markdown(
            f"""
            <div class="cvd-brand">
                <img src="data:image/png;base64,{logo}" alt="CVD Predictor logo" />
                <div>
                    <div class="cvd-brand-title">CVD Predictor</div>
                    <div class="cvd-brand-subtitle">Clinical AI Assistant</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def card(title: str, body: str, icon: str = "✚") -> None:
    st.markdown(
        f"""
        <div class="glass-card">
            <div style="font-size:1.5rem; color:#dc2626;">{icon}</div>
            <h3 style="margin:.25rem 0 .35rem;">{title}</h3>
            <p class="small-muted">{body}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
