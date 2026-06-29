"""Centralized theme tokens and CSS for the Streamlit UI."""

from __future__ import annotations

from typing import Dict

import streamlit as st

THEME: Dict[str, str] = {
    "primary": "#14B8A6",
    "primary_hover": "#0F9E90",
    "primary_deep": "#0B6E69",
    "accent": "#D4A72C",
    "accent_soft": "#F0D77A",
    "background": "#081316",
    "background_alt": "#0B171B",
    "surface": "rgba(15, 28, 32, 0.72)",
    "surface_strong": "rgba(18, 34, 38, 0.88)",
    "surface_soft": "rgba(10, 22, 26, 0.58)",
    "border": "rgba(255, 255, 255, 0.09)",
    "border_strong": "rgba(20, 184, 166, 0.28)",
    "text": "#E8F3F1",
    "text_muted": "#A4BBB7",
    "text_soft": "#708884",
    "success": "#22C55E",
    "success_soft": "rgba(34, 197, 94, 0.12)",
    "success_border": "rgba(34, 197, 94, 0.32)",
    "warning": "#D4A72C",
    "warning_soft": "rgba(212, 167, 44, 0.12)",
    "warning_border": "rgba(212, 167, 44, 0.32)",
    "error": "#EF4444",
    "error_soft": "rgba(239, 68, 68, 0.12)",
    "error_border": "rgba(239, 68, 68, 0.32)",
    "info": "#38BDF8",
    "shadow": "0 18px 50px rgba(0, 0, 0, 0.34)",
}


def get_theme_css() -> str:
    """Return the global CSS for the academic dark theme."""
    return f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700&display=swap');

    :root {{
        --lno-primary: {THEME["primary"]};
        --lno-primary-hover: {THEME["primary_hover"]};
        --lno-primary-deep: {THEME["primary_deep"]};
        --lno-accent: {THEME["accent"]};
        --lno-accent-soft: {THEME["accent_soft"]};
        --lno-bg: {THEME["background"]};
        --lno-bg-alt: {THEME["background_alt"]};
        --lno-surface: {THEME["surface"]};
        --lno-surface-strong: {THEME["surface_strong"]};
        --lno-surface-soft: {THEME["surface_soft"]};
        --lno-border: {THEME["border"]};
        --lno-border-strong: {THEME["border_strong"]};
        --lno-text: {THEME["text"]};
        --lno-text-muted: {THEME["text_muted"]};
        --lno-text-soft: {THEME["text_soft"]};
        --lno-success: {THEME["success"]};
        --lno-success-soft: {THEME["success_soft"]};
        --lno-success-border: {THEME["success_border"]};
        --lno-warning: {THEME["warning"]};
        --lno-warning-soft: {THEME["warning_soft"]};
        --lno-warning-border: {THEME["warning_border"]};
        --lno-error: {THEME["error"]};
        --lno-error-soft: {THEME["error_soft"]};
        --lno-error-border: {THEME["error_border"]};
        --lno-shadow: {THEME["shadow"]};
    }}

    html, body, [class*="css"] {{
        font-family: "IBM Plex Sans", "Source Sans Pro", sans-serif;
    }}

    [data-testid="stAppViewContainer"] {{
        background:
            radial-gradient(circle at top left, rgba(20, 184, 166, 0.14), transparent 30%),
            radial-gradient(circle at top right, rgba(212, 167, 44, 0.10), transparent 24%),
            linear-gradient(180deg, var(--lno-bg-alt) 0%, var(--lno-bg) 42%, #061014 100%);
        color: var(--lno-text);
    }}

    [data-testid="stHeader"] {{
        background: rgba(8, 19, 22, 0.72);
        border-bottom: 1px solid var(--lno-border);
    }}

    [data-testid="stSidebar"] {{
        background:
            linear-gradient(180deg, rgba(10, 24, 28, 0.94), rgba(6, 15, 18, 0.90));
        border-right: 1px solid var(--lno-border);
        backdrop-filter: blur(18px);
    }}

    [data-testid="stSidebar"] > div:first-child {{
        background: transparent;
    }}

    [data-testid="stSidebarNav"] {{
        display: none;
    }}

    .block-container {{
        padding-top: 2rem;
        padding-bottom: 2.5rem;
        max-width: 1220px;
    }}

    .page-shell {{
        margin-bottom: 1.4rem;
        padding: 1.4rem 1.5rem 1.2rem;
        border: 1px solid var(--lno-border);
        border-radius: 24px;
        background: linear-gradient(180deg, rgba(20, 34, 38, 0.72), rgba(11, 20, 24, 0.62));
        backdrop-filter: blur(18px);
        box-shadow: var(--lno-shadow);
    }}

    .page-eyebrow {{
        margin: 0 0 0.35rem;
        color: var(--lno-accent-soft);
        font-size: 0.8rem;
        font-weight: 600;
        letter-spacing: 0.14em;
        text-transform: uppercase;
    }}

    .page-title {{
        margin: 0;
        color: var(--lno-text);
        font-size: 2rem;
        font-weight: 700;
        letter-spacing: -0.03em;
    }}

    .page-description {{
        margin: 0.65rem 0 0;
        max-width: 52rem;
        color: var(--lno-text-muted);
        font-size: 1rem;
        line-height: 1.7;
    }}

    .upload-panel {{
        margin-bottom: 1rem;
        padding: 1.25rem 1.35rem;
        border: 1px solid var(--lno-border);
        border-radius: 24px;
        background: linear-gradient(180deg, rgba(17, 29, 33, 0.86), rgba(10, 19, 23, 0.68));
        box-shadow: var(--lno-shadow);
        backdrop-filter: blur(16px);
    }}

    .upload-intro {{
        text-align: center;
        margin-bottom: 1rem;
    }}

    .upload-icon {{
        font-size: 2.15rem;
        line-height: 1;
        color: var(--lno-primary);
    }}

    .upload-title {{
        margin: 0.55rem 0 0;
        color: var(--lno-text);
        font-size: 1.12rem;
        font-weight: 600;
    }}

    .upload-subtitle {{
        margin: 0.28rem 0 0;
        color: var(--lno-text-muted);
        font-size: 0.95rem;
    }}

    .upload-supported {{
        margin-top: 0.85rem;
        color: var(--lno-text-soft);
        font-size: 0.84rem;
        text-align: center;
        letter-spacing: 0.02em;
    }}

    .upload-preview {{
        margin-top: 1rem;
        padding: 1rem 1.1rem;
        border: 1px solid rgba(20, 184, 166, 0.18);
        border-radius: 20px;
        background: rgba(20, 184, 166, 0.05);
    }}

    .upload-preview-grid {{
        display: grid;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 0.9rem;
        margin-top: 0.8rem;
    }}

    .upload-preview-label {{
        color: var(--lno-text-soft);
        font-size: 0.76rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
    }}

    .upload-preview-value {{
        margin-top: 0.18rem;
        color: var(--lno-text);
        font-size: 0.95rem;
        font-weight: 500;
        word-break: break-word;
    }}

    .upload-action-row {{
        display: flex;
        justify-content: center;
        margin-top: 1.15rem;
    }}

    .meta-row {{
        display: flex;
        flex-wrap: wrap;
        gap: 0.5rem;
        align-items: center;
        margin: 0.4rem 0 0.9rem;
    }}

    .meta-pill {{
        display: inline-flex;
        align-items: center;
        gap: 0.35rem;
        padding: 0.35rem 0.8rem;
        border: 1px solid var(--lno-border);
        border-radius: 999px;
        background: rgba(255, 255, 255, 0.04);
        color: var(--lno-text-muted);
        font-size: 0.84rem;
    }}

    .meta-pill--accent {{
        border-color: rgba(212, 167, 44, 0.22);
        color: var(--lno-accent-soft);
        background: rgba(212, 167, 44, 0.08);
    }}

    .badge-row {{
        display: flex;
        flex-wrap: wrap;
        gap: 0.45rem;
        margin-top: 0.85rem;
    }}

    .topic-badge {{
        display: inline-flex;
        align-items: center;
        padding: 0.3rem 0.7rem;
        border: 1px solid rgba(20, 184, 166, 0.2);
        border-radius: 999px;
        background: rgba(20, 184, 166, 0.08);
        color: #C9F2EC;
        font-size: 0.8rem;
    }}

    .keyword-badge {{
        display: inline-flex;
        align-items: center;
        padding: 0.3rem 0.7rem;
        border: 1px solid rgba(212, 167, 44, 0.16);
        border-radius: 999px;
        background: rgba(212, 167, 44, 0.08);
        color: #F3E4AE;
        font-size: 0.8rem;
    }}

    .note-summary {{
        color: var(--lno-text-muted);
        line-height: 1.7;
        margin: 0.25rem 0 0;
    }}

    .section-label {{
        margin-top: 1rem;
        color: var(--lno-accent-soft);
        font-size: 0.79rem;
        font-weight: 600;
        letter-spacing: 0.08em;
        text-transform: uppercase;
    }}

    h1, h2, h3, h4, h5, h6, p, label, div, span {{
        color: inherit;
    }}

    [data-testid="stVerticalBlockBorderWrapper"] {{
        border: 1px solid var(--lno-border) !important;
        border-radius: 22px !important;
        background: linear-gradient(180deg, var(--lno-surface) 0%, var(--lno-surface-soft) 100%);
        box-shadow: var(--lno-shadow);
        backdrop-filter: blur(20px);
    }}

    [data-testid="stMetric"] {{
        padding: 0.9rem 1rem;
        border: 1px solid var(--lno-border);
        border-radius: 20px;
        background: linear-gradient(180deg, rgba(17, 29, 33, 0.88), rgba(11, 20, 24, 0.72));
        box-shadow: var(--lno-shadow);
    }}

    [data-testid="stMetricLabel"] p {{
        color: var(--lno-text-muted);
        font-weight: 500;
        letter-spacing: 0.01em;
    }}

    [data-testid="stMetricValue"] {{
        color: var(--lno-text);
        font-weight: 700;
    }}

    .stButton > button,
    [data-testid="stBaseButton-secondary"],
    [data-testid="stBaseButton-primary"] {{
        border-radius: 999px !important;
        border: 1px solid rgba(20, 184, 166, 0.2) !important;
        background: linear-gradient(180deg, rgba(19, 63, 67, 0.96), rgba(11, 44, 47, 0.94)) !important;
        color: var(--lno-text) !important;
        min-height: 2.8rem;
        padding: 0.55rem 1rem !important;
        transition: transform 160ms ease, box-shadow 160ms ease, background 160ms ease;
        box-shadow: 0 10px 24px rgba(0, 0, 0, 0.24);
    }}

    .stButton > button:hover,
    [data-testid="stBaseButton-secondary"]:hover,
    [data-testid="stBaseButton-primary"]:hover {{
        transform: translateY(-1px);
        background: linear-gradient(180deg, rgba(24, 88, 93, 0.98), rgba(13, 57, 60, 0.96)) !important;
        box-shadow: 0 14px 28px rgba(0, 0, 0, 0.28);
    }}

    .stButton > button[kind="secondary"] {{
        background: rgba(255, 255, 255, 0.04) !important;
    }}

    .stTextInput > div > div,
    .stNumberInput > div > div,
    .stSelectbox > div > div,
    .stTextArea > div > div,
    [data-baseweb="select"] > div,
    [data-testid="stFileUploaderDropzone"] {{
        border-radius: 18px !important;
        border: 1px solid var(--lno-border) !important;
        background: rgba(13, 25, 29, 0.78) !important;
        color: var(--lno-text) !important;
    }}

    [data-testid="stFileUploaderDropzone"] {{
        min-height: 11rem;
        padding: 2.25rem 1.5rem;
        border-style: dashed !important;
        border-width: 2px !important;
        background:
            linear-gradient(180deg, rgba(15, 31, 35, 0.86), rgba(9, 20, 24, 0.76)) !important;
        transition: border-color 160ms ease, background 160ms ease, transform 160ms ease;
    }}

    [data-testid="stFileUploaderDropzone"]:hover {{
        border-color: rgba(20, 184, 166, 0.42) !important;
        background:
            linear-gradient(180deg, rgba(17, 37, 42, 0.92), rgba(10, 24, 29, 0.82)) !important;
        transform: translateY(-1px);
    }}

    [data-testid="stFileUploaderDropzone"] > div {{
        align-items: center;
    }}

    [data-testid="stFileUploaderDropzone"] svg {{
        width: 2.1rem;
        height: 2.1rem;
        color: var(--lno-primary);
    }}

    [data-testid="stFileUploaderDropzoneInstructions"] > div {{
        color: var(--lno-text-muted) !important;
    }}

    [data-testid="stFileUploaderDropzone"] small {{
        color: var(--lno-text-soft) !important;
    }}

    .stSlider [data-baseweb="slider"] {{
        padding-top: 0.35rem;
    }}

    .stProgress > div > div > div > div {{
        background: linear-gradient(90deg, var(--lno-primary), var(--lno-accent)) !important;
        border-radius: 999px;
    }}

    .stProgress > div > div > div {{
        background: rgba(255, 255, 255, 0.08) !important;
        border-radius: 999px;
    }}

    [data-testid="stExpander"] {{
        border: 1px solid var(--lno-border) !important;
        border-radius: 20px !important;
        background: rgba(13, 24, 28, 0.58) !important;
    }}

    [data-testid="stAlert"] {{
        border-radius: 18px;
        border: 1px solid var(--lno-border);
        background: rgba(12, 26, 30, 0.84);
    }}

    [data-testid="stSidebar"] .stRadio > label {{
        color: var(--lno-text-muted);
        font-size: 0.82rem;
        font-weight: 600;
        letter-spacing: 0.08em;
        text-transform: uppercase;
    }}

    [data-testid="stSidebar"] .stRadio [role="radiogroup"] {{
        gap: 0.45rem;
    }}

    [data-testid="stSidebar"] .stRadio label[data-baseweb="radio"] {{
        width: 100%;
        margin: 0;
        padding: 0.85rem 0.95rem;
        border: 1px solid transparent;
        border-radius: 18px;
        background: rgba(255, 255, 255, 0.03);
        transition: background 160ms ease, border-color 160ms ease, transform 160ms ease;
    }}

    [data-testid="stSidebar"] .stRadio label[data-baseweb="radio"]:hover {{
        background: rgba(20, 184, 166, 0.08);
        border-color: rgba(20, 184, 166, 0.18);
        transform: translateX(2px);
    }}

    .sidebar-nav-label {{
        margin: 0 0 0.55rem;
        color: var(--lno-text-soft);
        font-size: 0.73rem;
        font-weight: 600;
        letter-spacing: 0.12em;
        text-transform: uppercase;
    }}

    [data-testid="stSidebar"] .stButton {{
        margin-bottom: 0.38rem;
    }}

    [data-testid="stSidebar"] .stButton > button {{
        justify-content: flex-start;
        min-height: 3rem;
        padding-inline: 1rem !important;
        border-radius: 16px !important;
        font-weight: 500;
        letter-spacing: 0.01em;
        box-shadow: none;
    }}

    [data-testid="stSidebar"] .stButton > button[kind="secondary"] {{
        border-color: transparent !important;
        background: rgba(255, 255, 255, 0.025) !important;
        color: var(--lno-text-muted) !important;
    }}

    [data-testid="stSidebar"] .stButton > button[kind="secondary"]:hover {{
        border-color: var(--lno-border-strong) !important;
        background: rgba(20, 184, 166, 0.08) !important;
        color: var(--lno-text) !important;
        transform: translateX(3px);
    }}

    .status-card {{
        display: flex;
        min-height: 12.2rem;
        padding: 1.1rem;
        flex-direction: column;
        border: 1px solid var(--lno-border);
        border-radius: 22px;
        background: linear-gradient(180deg, var(--lno-surface), var(--lno-surface-soft));
        color: var(--lno-text);
        text-decoration: none !important;
        box-shadow: var(--lno-shadow);
        transition: transform 180ms ease, border-color 180ms ease, box-shadow 180ms ease;
    }}

    .status-card:hover {{
        transform: translateY(-3px);
        border-color: var(--lno-border-strong);
        box-shadow: 0 22px 54px rgba(0, 0, 0, 0.4);
    }}

    .status-card--success {{ border-top-color: var(--lno-success); }}
    .status-card--warning {{ border-top-color: var(--lno-warning); }}
    .status-card--error {{ border-top-color: var(--lno-error); }}

    .status-card__top {{
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 0.75rem;
    }}

    .status-card__icon {{
        display: grid;
        width: 2.5rem;
        height: 2.5rem;
        place-items: center;
        border: 1px solid var(--lno-border);
        border-radius: 13px;
        background: rgba(255, 255, 255, 0.04);
        color: var(--lno-accent-soft);
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 0.06em;
    }}

    .status-badge {{
        display: inline-flex;
        align-items: center;
        width: fit-content;
        padding: 0.3rem 0.65rem;
        border: 1px solid;
        border-radius: 999px;
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.04em;
        text-transform: uppercase;
    }}

    .status-badge--success {{
        border-color: var(--lno-success-border);
        background: var(--lno-success-soft);
        color: var(--lno-success);
    }}

    .status-badge--warning {{
        border-color: var(--lno-warning-border);
        background: var(--lno-warning-soft);
        color: var(--lno-warning);
    }}

    .status-badge--error {{
        border-color: var(--lno-error-border);
        background: var(--lno-error-soft);
        color: var(--lno-error);
    }}

    .status-card__title {{
        margin-top: 1.1rem;
        color: var(--lno-text);
        font-size: 1.1rem;
        font-weight: 700;
    }}

    .status-card__detail {{
        margin-top: 0.35rem;
        color: var(--lno-text-muted);
        font-size: 0.86rem;
        line-height: 1.5;
    }}

    .status-card__action {{
        margin-top: auto;
        padding-top: 1rem;
        color: var(--lno-primary);
        font-size: 0.8rem;
        font-weight: 600;
    }}

    .stats-grid {{
        display: grid;
        grid-template-columns: repeat(4, minmax(0, 1fr));
        gap: 0.8rem;
        margin-bottom: 1.5rem;
    }}

    .stat-card {{
        min-width: 0;
        padding: 1.05rem;
        border: 1px solid var(--lno-border);
        border-radius: 20px;
        background: linear-gradient(180deg, var(--lno-surface), var(--lno-surface-soft));
        box-shadow: var(--lno-shadow);
    }}

    .stat-card__label {{
        color: var(--lno-text-muted);
        font-size: 0.76rem;
        font-weight: 600;
        letter-spacing: 0.04em;
        text-transform: uppercase;
    }}

    .stat-card__value {{
        margin-top: 0.55rem;
        overflow: hidden;
        color: var(--lno-text);
        font-size: 1.38rem;
        font-weight: 700;
        text-overflow: ellipsis;
        white-space: nowrap;
    }}

    .stat-card__hint {{
        margin-top: 0.35rem;
        color: var(--lno-text-soft);
        font-size: 0.76rem;
    }}

    .process-stepper {{
        display: grid;
        grid-template-columns: repeat(4, minmax(0, 1fr));
        gap: 0;
        margin: 1.1rem 0 1.25rem;
        padding: 1rem;
        border: 1px solid var(--lno-border);
        border-radius: 20px;
        background: var(--lno-surface-soft);
    }}

    .process-step {{
        position: relative;
        display: flex;
        align-items: center;
        gap: 0.7rem;
        min-width: 0;
    }}

    .process-step:not(:last-child)::after {{
        position: absolute;
        z-index: 0;
        top: 50%;
        right: 0.35rem;
        width: calc(100% - 8.7rem);
        height: 1px;
        background: var(--lno-border);
        content: "";
    }}

    .process-step__marker {{
        position: relative;
        z-index: 1;
        display: grid;
        width: 2rem;
        height: 2rem;
        flex: 0 0 2rem;
        place-items: center;
        border: 1px solid var(--lno-border);
        border-radius: 50%;
        background: var(--lno-bg-alt);
        color: var(--lno-text-soft);
        font-size: 0.7rem;
        font-weight: 700;
    }}

    .process-step__copy {{ display: flex; min-width: 0; flex-direction: column; }}
    .process-step__copy strong {{ color: var(--lno-text-muted); font-size: 0.8rem; }}
    .process-step__copy small {{ color: var(--lno-text-soft); font-size: 0.7rem; }}

    .process-step--active .process-step__marker {{
        border-color: var(--lno-primary);
        background: var(--lno-primary-deep);
        color: var(--lno-text);
        box-shadow: 0 0 0 5px rgba(20, 184, 166, 0.1);
    }}

    .process-step--active .process-step__copy strong {{ color: var(--lno-primary); }}
    .process-step--complete .process-step__marker {{
        border-color: var(--lno-success-border);
        background: var(--lno-success-soft);
        color: var(--lno-success);
    }}
    .process-step--error .process-step__marker {{
        border-color: var(--lno-error-border);
        background: var(--lno-error-soft);
        color: var(--lno-error);
    }}

    .status-list {{ display: grid; gap: 0.55rem; }}
    .status-list-row {{
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 1rem;
        padding: 0.65rem 0;
        border-bottom: 1px solid var(--lno-border);
        color: var(--lno-text-muted);
    }}

    .app-footer {{
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 1rem;
        margin-top: 2.5rem;
        padding: 1.1rem 0.2rem 0;
        border-top: 1px solid var(--lno-border);
    }}

    .app-footer__label {{
        color: var(--lno-text-soft);
        font-size: 0.78rem;
        font-weight: 600;
        letter-spacing: 0.08em;
        text-transform: uppercase;
    }}

    .app-footer__chips {{ display: flex; flex-wrap: wrap; gap: 0.45rem; justify-content: flex-end; }}
    .footer-chip {{
        padding: 0.3rem 0.65rem;
        border: 1px solid var(--lno-border);
        border-radius: 999px;
        background: rgba(255, 255, 255, 0.03);
        color: var(--lno-text-muted);
        font-size: 0.72rem;
    }}

    .sidebar-brand {{
        margin-bottom: 1.25rem;
        padding: 0.2rem 0 0.75rem;
    }}

    .sidebar-title {{
        margin: 0;
        color: var(--lno-text);
        font-size: 1.2rem;
        font-weight: 700;
        letter-spacing: -0.02em;
    }}

    .sidebar-subtitle {{
        margin: 0.35rem 0 0;
        color: var(--lno-text-muted);
        font-size: 0.9rem;
        line-height: 1.5;
    }}

    .sidebar-footer {{
        margin-top: 1.25rem;
        color: var(--lno-text-soft);
        font-size: 0.78rem;
        line-height: 1.6;
    }}

    hr {{
        border-color: var(--lno-border);
    }}

    code {{
        color: #DDF8F3;
        background: rgba(255, 255, 255, 0.06);
        border-radius: 8px;
        padding: 0.15rem 0.35rem;
    }}

    @media (max-width: 768px) {{
        .block-container {{
            padding-top: 1.2rem;
        }}

        .page-shell {{
            padding: 1.1rem 1rem;
            border-radius: 20px;
        }}

        .page-title {{
            font-size: 1.65rem;
        }}

        .upload-preview-grid {{
            grid-template-columns: 1fr;
        }}

        .stats-grid {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}

        .process-stepper {{ grid-template-columns: 1fr; gap: 0.8rem; }}
        .process-step:not(:last-child)::after {{ display: none; }}
        .app-footer {{ align-items: flex-start; flex-direction: column; }}
        .app-footer__chips {{ justify-content: flex-start; }}
    }}

    @media (max-width: 480px) {{
        .stats-grid {{ grid-template-columns: 1fr; }}
        [data-testid="stFileUploaderDropzone"] {{ min-height: 9rem; padding: 1.5rem 1rem; }}
    }}
    </style>
    """


def apply_theme() -> None:
    """Inject the shared CSS theme into the active Streamlit page."""
    st.markdown(get_theme_css(), unsafe_allow_html=True)
