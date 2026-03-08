# streamlit/app.py  — Overview / landing page
from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from utils.dashboard_utils import inject_css, load_data, page_header, section_divider, KPI_META

st.set_page_config(
    page_title="CDP Insights",
    page_icon="assets/favicon.png",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_css()
page_header("CDP Insights", "Operational Analytics & Reporting")

# ── load data for summary metrics ──────────────────────────────────────────
tables = load_data()

# ── summary banner ─────────────────────────────────────────────────────────
section_divider("At a Glance")

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.metric("KPIs Tracked", len(KPI_META))
with c2:
    txn = tables.get("kpi_01_transactions_created")
    st.metric("Transactions (Period)",
              int(txn["transactions_created"].sum()) if txn is not None else "—")
with c3:
    docs = tables.get("kpi_03_documents_executed")
    st.metric("Documents Executed (Period)",
              int(docs["documents_executed"].sum()) if docs is not None else "—")
with c4:
    users = tables.get("kpi_09_auth_users_touched_per_day")
    st.metric("Users Touched (Period)",
              int(users["users_touched"].sum()) if users is not None else "—")


# ── dashboard cards ────────────────────────────────────────────────────────
section_divider("Dashboards")

DASHBOARDS = [
    {
        "icon":        "📈",
        "title":       "Pipeline Health",
        "desc":        "Transactions → Documents → Execution rate funnel. Track deal velocity and conversion at every stage.",
        "color":       "#6366F1",
        "page":        "pages/01_pipeline_health.py",
        "link_label":  "Open Pipeline Health →",
        "kpis":        "KPI 01 · KPI 02 · KPI 03 · KPI 04",
    },
    {
        "icon":        "✍️",
        "title":       "eSign & Engagement",
        "desc":        "Parties per transaction and eSign funnel events. See who's signing and where drop-off happens.",
        "color":       "#8B5CF6",
        "page":        "pages/02_esign_engagement.py",
        "link_label":  "Open eSign & Engagement →",
        "kpis":        "KPI 05 · KPI 06",
    },
    {
        "icon":        "👥",
        "title":       "User Activity & Consent",
        "desc":        "TCPA consent compliance, users updated daily, and the Long Realty activity window.",
        "color":       "#0EA5E9",
        "page":        "pages/03_user_activity.py",
        "link_label":  "Open User Activity →",
        "kpis":        "KPI 07 · KPI 09 · KPI 10",
    },
    {
        "icon":        "⚡",
        "title":       "Speed & Survey",
        "desc":        "Time from transaction creation to full execution, and PHM survey boolean outcomes.",
        "color":       "#F97316",
        "page":        "pages/04_speed_survey.py",
        "link_label":  "Open Speed & Survey →",
        "kpis":        "KPI 08 · KPI 11",
    },
]

cols = st.columns(4)

for col, d in zip(cols, DASHBOARDS):
    with col:
        st.markdown(
            f"""
            <div style="
                border: 1px solid rgba(0,0,0,0.08);
                border-top: 4px solid {d['color']};
                border-radius: 12px;
                padding: 1.2rem 1.3rem 0.6rem 1.3rem;
                box-shadow: 0 1px 4px rgba(0,0,0,0.05);
                min-height: 180px;
            ">
                <div style="font-size:1.7rem; margin-bottom:6px;">{d['icon']}</div>
                <div style="font-weight:800; font-size:1.05rem;
                            margin-bottom:6px;">{d['title']}</div>
                <div style="color:#6B7280; font-size:0.82rem;
                            line-height:1.55; margin-bottom:10px;">{d['desc']}</div>
                <div style="
                    display:inline-block;
                    background:{d['color']}18;
                    color:{d['color']};
                    font-size:0.7rem;
                    font-weight:700;
                    letter-spacing:0.06em;
                    padding:2px 8px;
                    border-radius:20px;
                    margin-bottom:12px;
                ">{d['kpis']}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        # native Streamlit page link — sits just below each card
        st.page_link(d["page"], label=d["link_label"], icon=d["icon"])


# ── footer ─────────────────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
section_divider("About")
st.caption(
    "CDP Insights · Built with Streamlit · "
    "Data sourced from `kpis.zip` · "
    "Navigate using the sidebar or the links above."
)