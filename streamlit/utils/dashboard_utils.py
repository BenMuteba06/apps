# streamlit/utils/dashboard_utils.py
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import streamlit as st

# ── repo root on path ──────────────────────────────────────────────────────
_ROOT = Path(__file__).resolve().parent.parent.parent  # apps/
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from io_layer.data_loader import DataSourceConfig, load_tables

# ── paths ──────────────────────────────────────────────────────────────────
_ZIP_PATH    = Path(__file__).resolve().parent.parent / "assets" / "kpis.zip"
_EXTRACT_DIR = Path(__file__).resolve().parent.parent.parent / ".cache" / "kpi_unzipped"


# ── data loading ───────────────────────────────────────────────────────────
def load_data() -> dict:
    cfg = DataSourceConfig(
        source_path=str(_ZIP_PATH),
        extract_to=str(_EXTRACT_DIR),
        recurse=True,
        clean_names=True,
    )
    return load_tables(cfg)


def get_table(tables: dict, name: str) -> pd.DataFrame:
    if name not in tables:
        available = ", ".join(tables.keys())
        raise KeyError(f"Table '{name}' not found. Available: {available}")
    return tables[name].copy()


# ── KPI metadata ───────────────────────────────────────────────────────────
KPI_META = {
    "kpi01": {
        "title": "KPI 01 — Transactions Created / Day",
        "badge": "Volume",
        "badge_color": "#6366F1",
        "description": "Count of new transactions created each day.",
    },
    "kpi02": {
        "title": "KPI 02 — Documents Generated / Day",
        "badge": "Volume",
        "badge_color": "#6366F1",
        "description": "Count of documents created for those transactions.",
    },
    "kpi03": {
        "title": "KPI 03 — Documents Executed / Day",
        "badge": "Completion",
        "badge_color": "#10B981",
        "description": "Count of documents fully signed — all required signers completed.",
    },
    "kpi04": {
        "title": "KPI 04 — Execution Rate / Day",
        "badge": "Conversion",
        "badge_color": "#F59E0B",
        "description": "Executed ÷ Generated. Conversion rate from document created to fully signed.",
    },
    "kpi05": {
        "title": "KPI 05 — Borrowers / Parties per Transaction",
        "badge": "Engagement",
        "badge_color": "#3B82F6",
        "description": "How many unique parties and signer emails are involved per transaction.",
    },
    "kpi06": {
        "title": "KPI 06 — eSign Funnel Events / Day",
        "badge": "Funnel",
        "badge_color": "#8B5CF6",
        "description": "Counts of envelope sent, delivered, and completed from eSign audit events.",
    },
    "kpi07": {
        "title": "KPI 07 — TCPA Consent / Day",
        "badge": "Compliance",
        "badge_color": "#EF4444",
        "description": "Count of yes / no communication consent responses captured per day.",
    },
    "kpi08": {
        "title": "KPI 08 — Time to Execution",
        "badge": "Speed",
        "badge_color": "#F97316",
        "description": "Median and P95 time from transaction creation to full execution — measures speed and friction.",
    },
    "kpi09": {
        "title": "KPI 09 — Long Realty Users Window",
        "badge": "Coverage",
        "badge_color": "#14B8A6",
        "description": "Earliest and latest time any user in the scoped set was ever touched, and the total user count.",
    },
    "kpi10": {
        "title": "KPI 10 — Users Updated / Day",
        "badge": "Activity",
        "badge_color": "#0EA5E9",
        "description": "Count of users whose auth record changed that day. Not logins — includes system updates.",
    },
    "kpi11": {
        "title": "KPI 11 — PHM Survey Question Counts",
        "badge": "Survey",
        "badge_color": "#EC4899",
        "description": "Counts of true / false / missing answers inside the stored PHM survey JSON.",
    },
}


# ── shared UI components ───────────────────────────────────────────────────
def kpi_header(key: str):
    m = KPI_META[key]
    st.markdown(
        f"""
        <div style="
            background: linear-gradient(135deg, {m['badge_color']}18 0%, transparent 70%);
            border-left: 4px solid {m['badge_color']};
            border-radius: 10px;
            padding: 1rem 1.25rem 0.85rem 1.25rem;
            margin-bottom: 1.1rem;
        ">
            <div style="display:flex; align-items:center; gap:10px; margin-bottom:4px;">
                <span style="
                    background:{m['badge_color']};
                    color:#fff;
                    font-size:0.68rem;
                    font-weight:700;
                    letter-spacing:0.08em;
                    padding:2px 10px;
                    border-radius:20px;
                    text-transform:uppercase;
                ">{m['badge']}</span>
                <span style="font-size:1.15rem; font-weight:700; letter-spacing:0.01em;">{m['title']}</span>
            </div>
            <p style="margin:0; color:#6B7280; font-size:0.9rem; line-height:1.5;">{m['description']}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def inject_css():
    st.markdown(
        """
        <style>
        .main > div { padding-top: 1rem; }
        .stCard {
            background: var(--background-color);
            border: 1px solid rgba(0,0,0,0.06);
            border-radius: 10px;
            padding: 1rem 1.25rem;
            box-shadow: 0 1px 2px rgba(0,0,0,0.04);
        }
        h1, h2, h3 { letter-spacing: 0.2px; }
        [data-testid="metric-container"] {
            background: var(--background-color);
            border: 1px solid rgba(0,0,0,0.07);
            border-radius: 10px;
            padding: 1rem 1.25rem;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def page_header(title: str, subtitle: str):
    """Render a consistent top-of-page header for every dashboard."""
    from datetime import datetime
    left, right = st.columns([0.78, 0.22])
    with left:
        st.markdown(
            f"""
            <div style="display:flex; align-items:baseline; gap:12px; margin-bottom:2px;">
                <span style="font-size:1.55rem; font-weight:800; letter-spacing:-0.01em;">{title}</span>
                <span style="color:#9CA3AF; font-size:0.95rem;">{subtitle}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with right:
        st.caption(datetime.now().strftime("Updated %b %d, %Y %I:%M %p"))
    st.markdown("<hr style='margin:6px 0 20px 0; opacity:0.15;'>", unsafe_allow_html=True)


def section_divider(label: str):
    """Subtle labelled divider between chart sections."""
    st.markdown(
        f"""
        <div style="display:flex; align-items:center; gap:12px; margin:1.6rem 0 1rem 0;">
            <span style="font-size:0.78rem; font-weight:700; text-transform:uppercase;
                         letter-spacing:0.1em; color:#9CA3AF;">{label}</span>
            <div style="flex:1; height:1px; background:rgba(0,0,0,0.08);"></div>
        </div>
        """,
        unsafe_allow_html=True,
    )