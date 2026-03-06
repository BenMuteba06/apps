# streamlit/app.py
from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st

# ── make sure repo root (apps/) is importable ──────────────────────────────
_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from io_layer.data_loader import DataSourceConfig, load_tables
from transforms import kpi01, kpi02, kpi03, kpi04, kpi05, kpi06, kpi07, kpi08, kpi09, kpi10, kpi11

# ── paths ──────────────────────────────────────────────────────────────────
_ZIP_PATH    = Path(__file__).resolve().parent / "assets" / "kpis.zip"
_EXTRACT_DIR = Path(__file__).resolve().parent.parent / ".cache" / "kpi_unzipped"


# ── page config ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="CDP Insights",
    page_icon="assets/favicon.png",
    layout="wide",
    initial_sidebar_state="expanded",
)


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


# ── CSS ────────────────────────────────────────────────────────────────────
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
        "description": "Count of users whose auth record changed that day (auth_users.updated_at). Not logins — includes system updates.",
    },
    "kpi11": {
        "title": "KPI 11 — PHM Survey Question Counts",
        "badge": "Survey",
        "badge_color": "#EC4899",
        "description": "Counts of true / false / missing answers inside the stored PHM survey JSON.",
    },
}


def kpi_header(key: str):
    """Render a modern styled header block for a KPI section."""
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
        </style>
        """,
        unsafe_allow_html=True,
    )


# ── header ─────────────────────────────────────────────────────────────────
def header():
    left, right = st.columns([0.8, 0.2])
    with left:
        st.markdown(
            """
            <div style="display:flex; align-items:center; gap:12px;">
                <span style="font-size:1.6rem; font-weight:700;">CDP Insights</span>
                <span style="color:#6b7280;">Operational Analytics & Reporting</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with right:
        st.caption(datetime.now().strftime("Last refreshed: %b %d, %Y %I:%M %p"))
    st.markdown("<hr style='margin-top:6px;margin-bottom:18px;'>", unsafe_allow_html=True)


# ── sidebar ────────────────────────────────────────────────────────────────
def sidebar():
    st.sidebar.title("Navigation")
    PAGES = {
        "Overview":                             overview_section,
        "KPI 01 – Transactions Created":        kpi01_section,
        "KPI 02 – Documents Generated":         kpi02_section,
        "KPI 03 – Documents Executed":          kpi03_section,
        "KPI 04 – Daily Execution Rate":        kpi04_section,
        "KPI 05 – Parties per Transaction":     kpi05_section,
        "KPI 06 – Envelope & Recipient Events": kpi06_section,
        "KPI 07 – TCPA Consent":                kpi07_section,
        "KPI 08 – Time to Txn Execution":       kpi08_section,
        "KPI 09 – Long Realty Users Window":    kpi09_section,
        "KPI 10 – Users Touched (Daily)":       kpi10_section,
        "KPI 11 – Boolean Outcomes (Daily)":    kpi11_section,
    }
    selected = st.sidebar.radio("Go to", list(PAGES.keys()), index=0, label_visibility="collapsed")
    return selected, PAGES[selected]


# ── overview ───────────────────────────────────────────────────────────────
def overview_section(tables: dict):
    st.subheader("Overview")
    st.write("Welcome to **CDP Insights** — a streamlined interface for data exploration, KPIs, and operational dashboards.")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("**Active Sources**")
        st.markdown("<div class='stCard'><h3>12</h3><span>ingesting</span></div>", unsafe_allow_html=True)
    with c2:
        st.markdown("**Daily Records**")
        st.markdown("<div class='stCard'><h3>2.4K</h3><span>processed</span></div>", unsafe_allow_html=True)
    with c3:
        st.markdown("**Pipeline Health**")
        st.markdown("<div class='stCard'><h3>58.3%</h3><span>success rate</span></div>", unsafe_allow_html=True)


# ── KPI 01 ─────────────────────────────────────────────────────────────────
def kpi01_section(tables: dict):
    #st.subheader("KPI 01 – Transactions Created (Daily)")
    kpi_header("kpi01")
    df = kpi01.transform(get_table(tables, "kpi_01_transactions_created"))

    with st.expander("Show data", expanded=False):
        st.dataframe(df, width='stretch')

    chart = (
        alt.Chart(df).mark_line(point=True)
        .encode(
            x=alt.X("day:T", title="Day"),
            y=alt.Y("transactions_created:Q", title="Transactions Created"),
            tooltip=[alt.Tooltip("day:T", title="Day"),
                     alt.Tooltip("transactions_created:Q", title="Transactions")],
        )
        .properties(height=320).interactive()
    )
    st.altair_chart(chart, width='stretch')


# ── KPI 02 ─────────────────────────────────────────────────────────────────
def kpi02_section(tables: dict):
    #st.subheader("KPI 02 – Documents Generated (Daily)")
    kpi_header("kpi02")
    df = kpi02.transform(get_table(tables, "kpi_02_documents_generated"))

    with st.expander("Show data", expanded=False):
        st.dataframe(df, width='stretch')

    chart = (
        alt.Chart(df).mark_line(point=True)
        .encode(
            x=alt.X("day:T", title="Day"),
            y=alt.Y("documents_generated:Q", title="Documents Generated"),
            tooltip=[alt.Tooltip("day:T", title="Day"),
                     alt.Tooltip("documents_generated:Q", title="Documents")],
        )
        .properties(height=320).interactive()
    )
    st.altair_chart(chart, width='stretch')


# ── KPI 03 ─────────────────────────────────────────────────────────────────
def kpi03_section(tables: dict):
    #st.subheader("KPI 03 – Documents Executed (Daily)")
    kpi_header("kpi03")
    df = kpi03.transform(get_table(tables, "kpi_03_documents_executed"))

    with st.expander("Show data", expanded=False):
        st.dataframe(df, width='stretch')

    chart = (
        alt.Chart(df).mark_line(point=True)
        .encode(
            x=alt.X("day:T", title="Day"),
            y=alt.Y("documents_executed:Q", title="Documents Executed"),
            tooltip=[alt.Tooltip("day:T", title="Day"),
                     alt.Tooltip("documents_executed:Q", title="Documents")],
        )
        .properties(height=320).interactive()
    )
    st.altair_chart(chart, width='stretch')


# ── KPI 04 ─────────────────────────────────────────────────────────────────
def kpi04_section(tables: dict):
    #st.subheader("KPI 04 – Daily Execution Rate (Generated vs Executed + Rate)")
    kpi_header("kpi04")
    df = kpi04.transform(get_table(tables, "kpi_04_daily_execution_rate"))

    with st.expander("Show data", expanded=False):
        st.dataframe(df, width='stretch')

    base = alt.Chart(df).encode(x=alt.X("day:T", title="Day", axis=alt.Axis(labelAngle=0)))

    bars = (
        base
        .transform_fold(["generated", "executed"], as_=["metric", "value"])
        .mark_bar(opacity=0.5)
        .encode(
            y=alt.Y("value:Q", title="Count"),
            color=alt.Color("metric:N",
                            scale=alt.Scale(domain=["generated", "executed"],
                                            range=["#9CA3AF", "#10B981"]), title=""),
            xOffset="metric:N",
            tooltip=[alt.Tooltip("day:T"), alt.Tooltip("metric:N"), alt.Tooltip("value:Q")],
        )
    )

    rate_line = (
        base.mark_line(point=True, color="#2563EB")
        .encode(
            y=alt.Y("execution_rate:Q", title="Execution Rate",
                    axis=alt.Axis(orient="right", format=".0%"),
                    scale=alt.Scale(domain=[0, 1])),
            tooltip=[alt.Tooltip("day:T"), alt.Tooltip("execution_rate:Q", format=".2%")],
        )
    )

    rate_labels = (
        base.mark_text(align="center", dy=-10, color="#2563EB")
        .encode(
            y=alt.Y("execution_rate:Q", scale=alt.Scale(domain=[0, 1])),
            text=alt.Text("execution_rate:Q", format=".0%"),
        )
    )

    ref_rules = (
        alt.Chart(pd.DataFrame({"y": [0.5, 0.8, 1.0]}))
        .mark_rule(strokeDash=[4, 4], color="#EF4444")
        .encode(y="y:Q")
    )

    st.altair_chart(
        alt.layer(bars, ref_rules, rate_line, rate_labels)
        .resolve_scale(y="independent").properties(height=280),
        width='stretch',
    )


# ── KPI 05 ─────────────────────────────────────────────────────────────────
def kpi05_section(tables: dict):
    #st.subheader("KPI 05 – Parties per Transaction")
    kpi_header("kpi05")
    df = kpi05.transform(get_table(tables, "kpi_05_parties_per_transaction"))

    with st.expander("Show data", expanded=False):
        st.dataframe(df, width='stretch')

    st.markdown("#### Relationship: Parties on Docs vs. Signer Emails")
    max_axis = max(df["distinct_parties_on_docs"].max(), df["distinct_signer_emails"].max())
    points = (
        alt.Chart(df).mark_circle(size=110, color="#2563EB", opacity=0.75)
        .encode(
            x=alt.X("distinct_parties_on_docs:Q", title="Distinct Parties on Documents"),
            y=alt.Y("distinct_signer_emails:Q", title="Distinct Signer Emails"),
            tooltip=[alt.Tooltip("transaction_id:N"),
                     alt.Tooltip("distinct_parties_on_docs:Q"),
                     alt.Tooltip("distinct_signer_emails:Q"),
                     alt.Tooltip("party_email_delta:Q")],
        )
    )
    eq_line = (
        alt.Chart(pd.DataFrame({"x": [0, max_axis], "y": [0, max_axis]}))
        .mark_line(color="#9CA3AF", strokeDash=[6, 4]).encode(x="x:Q", y="y:Q")
    )
    st.altair_chart(alt.layer(eq_line, points).properties(height=320), width='stretch')

    st.markdown("#### Distribution of Parties per Transaction")
    st.altair_chart(
        alt.Chart(df).mark_bar(color="#10B981", opacity=0.8)
        .encode(x=alt.X("distinct_parties_on_docs:Q", title="Distinct Parties"),
                y=alt.Y("count():Q", title="Transactions"),
                tooltip=[alt.Tooltip("distinct_parties_on_docs:Q"), alt.Tooltip("count():Q")])
        .properties(height=220),
        width='stretch',
    )

    c1, c2, c3 = st.columns(3)
    with c1: st.metric("Transactions", len(df))
    with c2: st.metric("Mode: Parties per Tx", int(df["distinct_parties_on_docs"].mode().iloc[0]))
    with c3: st.metric("Pct Parties == Emails", f"{(df['party_email_delta']==0).mean():.0%}")


# ── KPI 06 ─────────────────────────────────────────────────────────────────
def kpi06_section(tables: dict):
    #st.subheader("KPI 06 – Envelope & Recipient Events (Daily)")
    kpi_header("kpi06")
    df = kpi06.transform(get_table(tables, "kpi_06_esign_funnel_events"))

    with st.expander("Show data", expanded=False):
        st.dataframe(df, width='stretch')

    base = alt.Chart(df).encode(x=alt.X("day:T", title="Day", axis=alt.Axis(labelAngle=0)))
    bar_metrics = ["envelope_sent", "recipient_delivered", "recipient_completed", "envelope_completed"]

    bars = (
        base.transform_fold(bar_metrics, as_=["metric", "value"]).mark_bar(opacity=0.6)
        .encode(
            y=alt.Y("value:Q", title="Count"),
            color=alt.Color("metric:N",
                            scale=alt.Scale(domain=bar_metrics,
                                            range=["#6B7280", "#6366F1", "#10B981", "#F59E0B"]), title=""),
            xOffset="metric:N",
            tooltip=[alt.Tooltip("day:T"), alt.Tooltip("metric:N"), alt.Tooltip("value:Q")],
        )
    )
    total_line = (
        base.mark_line(point=True, color="#2563EB")
        .encode(y=alt.Y("total_events:Q", title="Total Events", axis=alt.Axis(orient="right")),
                tooltip=[alt.Tooltip("day:T"), alt.Tooltip("total_events:Q")])
    )
    st.altair_chart(
        alt.layer(bars, total_line).resolve_scale(y="independent").properties(height=320),
        width='stretch',
    )

    c1, c2, c3, c4 = st.columns(4)
    with c1: st.metric("Avg Total Events", f"{df['total_events'].mean():.1f}")
    with c2: st.metric("Max Total Events", int(df["total_events"].max()))
    with c3: st.metric("Days (Range)", f"{df['day'].min().date()} → {df['day'].max().date()}")
    with c4: st.metric("Observations", len(df))


# ── KPI 07 ─────────────────────────────────────────────────────────────────
def kpi07_section(tables: dict):
    #st.subheader("KPI 07 – TCPA Consent (Daily)")
    kpi_header("kpi07")
    df = kpi07.transform(get_table(tables, "kpi_07_tcpa_consent_per_day"))

    with st.expander("Show data", expanded=False):
        st.dataframe(df, width='stretch')

    base = alt.Chart(df).encode(x=alt.X("day:T", title="Day", axis=alt.Axis(labelAngle=0)))
    bars = (
        base.transform_fold(["tcpa_yes", "tcpa_no"], as_=["metric", "value"]).mark_bar(opacity=0.70)
        .encode(
            y=alt.Y("value:Q", title="Count"),
            color=alt.Color("metric:N",
                            scale=alt.Scale(domain=["tcpa_yes", "tcpa_no"],
                                            range=["#10B981", "#EF4444"]), title=""),
            xOffset="metric:N",
            tooltip=[alt.Tooltip("day:T"), alt.Tooltip("metric:N"), alt.Tooltip("value:Q")],
        )
    )
    total_line = (
        base.mark_line(point=True, color="#2563EB")
        .encode(y=alt.Y("total_records:Q", title="Total Records", axis=alt.Axis(orient="right")),
                tooltip=[alt.Tooltip("day:T"), alt.Tooltip("total_records:Q")])
    )
    st.altair_chart(
        alt.layer(bars, total_line).resolve_scale(y="independent").properties(height=320),
        width='stretch',
    )

    c1, c2, c3, c4 = st.columns(4)
    with c1: st.metric("Total Records", int(df["total_records"].sum()))
    with c2: st.metric("TCPA Yes (Sum)", int(df["tcpa_yes"].sum()))
    with c3: st.metric("TCPA No (Sum)", int(df["tcpa_no"].sum()))
    with c4: st.metric("Yes Share", f"{df['tcpa_yes'].sum()/max(df['total_records'].sum(),1):.0%}")


# ── KPI 08 helpers ─────────────────────────────────────────────────────────
def _fmt_mmss(seconds: float) -> str:
    m = int(seconds // 60)
    s = seconds - m * 60
    return f"{m}:{s:04.1f}"


# ── KPI 08 ─────────────────────────────────────────────────────────────────
def kpi08_section(tables: dict):
    #st.subheader("KPI 08 – Time to Transaction Execution")
    kpi_header("kpi08")
    df = kpi08.transform(get_table(tables, "kpi_08_time_to_transaction_execution"))
    if df.empty:
        st.warning("No KPI 08 data available.")
        return

    row = df.iloc[0]
    c1, c2, c3 = st.columns(3)
    with c1: st.metric("Executed Transactions", int(row["executed_transactions"]))
    with c2: st.metric("Median Time to Execution", _fmt_mmss(row["median_seconds"]))
    with c3: st.metric("P95 Time to Execution", _fmt_mmss(row["p95_seconds"]))

    chart_df = pd.DataFrame({
        "metric":  ["Median", "P95"],
        "minutes": [float(row["median_minutes"]), float(row["p95_minutes"])],
        "label":   [_fmt_mmss(row["median_seconds"]), _fmt_mmss(row["p95_seconds"])],
    })
    scale_max = max(chart_df["minutes"].max(), 1.0) * 1.15

    bars = (
        alt.Chart(chart_df).mark_bar(cornerRadius=4)
        .encode(
            x=alt.X("minutes:Q", title="Minutes", scale=alt.Scale(domain=[0, scale_max])),
            y=alt.Y("metric:N", title="", sort=["P95", "Median"]),
            color=alt.Color("metric:N",
                            scale=alt.Scale(domain=["Median", "P95"], range=["#10B981", "#2563EB"]),
                            legend=None),
            tooltip=[alt.Tooltip("metric:N"), alt.Tooltip("minutes:Q", format=".1f"),
                     alt.Tooltip("label:N", title="Time")],
        ).properties(height=140)
    )
    labels = (
        alt.Chart(chart_df).mark_text(align="left", dx=6, color="#111827")
        .encode(x=alt.X("minutes:Q", scale=alt.Scale(domain=[0, scale_max])),
                y=alt.Y("metric:N", sort=["P95", "Median"]),
                text=alt.Text("label:N"))
    )
    st.altair_chart(bars + labels, width='stretch')


# ── KPI 09 helpers ─────────────────────────────────────────────────────────
def _fmt_span(days: float) -> str:
    total_minutes = int(round(days * 24 * 60))
    d, rem = divmod(total_minutes, 24 * 60)
    hh, mm = divmod(rem, 60)
    return f"{d} day{'s' if d!=1 else ''}, {hh:02d}:{mm:02d}" if d > 0 else f"{hh:02d}:{mm:02d}"


# ── KPI 09 ─────────────────────────────────────────────────────────────────
def kpi09_section(tables: dict):
    #st.subheader("KPI 09 – Long Realty Users Activity Window")
    kpi_header("kpi09")
    df = kpi09.transform(get_table(tables, "kpi_09_auth_first_seen_summary"))
    if df.empty or df["first_seen_ts"].isna().all():
        st.warning("No KPI 09 data available.")
        return

    row = df.iloc[0]
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.metric("First Seen (UTC)", row["first_seen_ts"].strftime("%Y-%m-%d %H:%M"))
    with c2: st.metric("Last Seen (UTC)",  row["last_seen_ts"].strftime("%Y-%m-%d %H:%M"))
    with c3: st.metric("Long Realty Users", int(row["long_realty_users"]))
    with c4: st.metric("Active Span", _fmt_span(float(row["span_days"])))

    timeline_df = pd.DataFrame({
        "label": ["Active Window"],
        "start": [pd.to_datetime(row["first_seen_ts"])],
        "end":   [pd.to_datetime(row["last_seen_ts"])],
    })
    bar = (
        alt.Chart(timeline_df).mark_bar(height=24, cornerRadius=6, color="#2563EB")
        .encode(x=alt.X("start:T", title=""), x2="end:T", y=alt.Y("label:N", title=""))
        .properties(height=70)
    )
    ticks = (
        alt.Chart(timeline_df)
        .transform_fold(["start", "end"], as_=["kind", "time"])
        .mark_tick(thickness=2, size=24, color="#111827")
        .encode(x="time:T", y="label:N",
                tooltip=[alt.Tooltip("kind:N"), alt.Tooltip("time:T")])
    )
    st.altair_chart(bar + ticks, width='stretch')

    with st.expander("Show raw KPI 09 data"):
        st.dataframe(
            df[["first_seen_ts","last_seen_ts","long_realty_users","span_hours","span_days"]],
            width='stretch',
        )


# ── KPI 10 ─────────────────────────────────────────────────────────────────
def kpi10_section(tables: dict):
    #st.subheader("KPI 10 – Users Touched (Daily)")
    kpi_header("kpi10")
    df = kpi10.transform(get_table(tables, "kpi_09_auth_users_touched_per_day"))

    c1, c2, c3 = st.columns(3)
    with c1: st.metric("Total (Range)", int(df["users_touched"].sum()))
    with c2: st.metric("Average / Day", f"{df['users_touched'].mean():.1f}")
    with c3: st.metric("Max in a Day", int(df["users_touched"].max()))

    with st.expander("Show data", expanded=False):
        st.dataframe(df, width='stretch')

    base = alt.Chart(df).encode(x=alt.X("day:T", title="Day", axis=alt.Axis(labelAngle=0)))
    daily = (
        base.mark_line(point=True, color="#2563EB")
        .encode(y=alt.Y("users_touched:Q", title="Users Touched"),
                tooltip=[alt.Tooltip("day:T"), alt.Tooltip("users_touched:Q")])
    )
    rolling = (
        base.mark_line(color="#10B981", strokeDash=[6, 4])
        .encode(y=alt.Y("7d_rolling:Q", title="7-day Rolling Avg"),
                tooltip=[alt.Tooltip("day:T"), alt.Tooltip("7d_rolling:Q", format=".1f")])
    )
    st.altair_chart(alt.layer(daily, rolling).properties(height=320), width='stretch')


# ── KPI 11 ─────────────────────────────────────────────────────────────────
def kpi11_section(tables: dict):
    #st.subheader("KPI 11 – Boolean Attribute Outcomes (Daily)")
    kpi_header("kpi11")
    df = kpi11.transform(get_table(tables, "kpi_10_phm_survey_question_counts"))
    if df.empty:
        st.warning("No KPI 11 data available.")
        return

    metrics = sorted(df["metric"].unique().tolist())
    for metric_name, tab in zip(metrics, st.tabs(metrics)):
        with tab:
            mdf = df[df["metric"] == metric_name].copy()
            if not mdf["event_date"].isna().all():
                mdf = mdf.sort_values("event_date").set_index("event_date")
                mdf = mdf.reindex(pd.date_range(mdf.index.min(), mdf.index.max(), freq="D"))
                mdf = mdf.rename_axis("event_date").reset_index()
                # fill numerics with 0, restore metric name (lost during reindex)
                for col in ["true_count", "false_count", "missing_count"]:
                    mdf[col] = mdf[col].fillna(0.0)
                mdf["metric"] = mdf["metric"].fillna(metric_name)

            c1, c2, c3, c4 = st.columns(4)
            with c1: st.metric("Days in Range", len(mdf))
            with c2: st.metric("True (Σ)",    int(mdf["true_count"].sum()))
            with c3: st.metric("False (Σ)",   int(mdf["false_count"].sum()))
            with c4: st.metric("Missing (Σ)", int(mdf["missing_count"].sum()))

            with st.expander("Show data", expanded=False):
                st.dataframe(mdf, width='stretch')

            plot_df = mdf.melt(id_vars=["event_date"],
                               value_vars=["true_count","false_count","missing_count"],
                               var_name="outcome", value_name="count")
            st.altair_chart(
                alt.Chart(plot_df).mark_bar()
                .encode(
                    x=alt.X("event_date:T", title="Date", axis=alt.Axis(labelAngle=0)),
                    y=alt.Y("count:Q", title=f"{metric_name} — Count"),
                    color=alt.Color("outcome:N",
                                    scale=alt.Scale(domain=["true_count","false_count","missing_count"],
                                                    range=["#10B981","#EF4444","#9CA3AF"]), title="Outcome"),
                    tooltip=[alt.Tooltip("event_date:T"), alt.Tooltip("outcome:N"), alt.Tooltip("count:Q")],
                ).properties(height=320),
                width='stretch',
            )


# ── entrypoint ─────────────────────────────────────────────────────────────
def main():
    inject_css()
    header()
    page_label, page_handler = sidebar()

    tables = load_data()
    page_handler(tables)


if __name__ == "__main__":
    main()