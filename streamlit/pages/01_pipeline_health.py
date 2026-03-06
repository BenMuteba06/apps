# streamlit/pages/01_pipeline_health.py
from __future__ import annotations

import sys
from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))  # apps/
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))          # streamlit/

from utils.dashboard_utils import (
    inject_css, load_data, get_table,
    kpi_header, page_header, section_divider,
)
from transforms import kpi01, kpi02, kpi03, kpi04

st.set_page_config(
    page_title="Pipeline Health — CDP Insights",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_css()
page_header("📈 Pipeline Health", "Transactions · Documents · Execution")

# ── load & transform ───────────────────────────────────────────────────────
tables = load_data()
df01 = kpi01.transform(get_table(tables, "kpi_01_transactions_created"))
df02 = kpi02.transform(get_table(tables, "kpi_02_documents_generated"))
df03 = kpi03.transform(get_table(tables, "kpi_03_documents_executed"))
df04 = kpi04.transform(get_table(tables, "kpi_04_daily_execution_rate"))

# ── date range filter ──────────────────────────────────────────────────────
all_days = pd.concat([df01["day"], df02["day"], df03["day"], df04["day"]])
min_date, max_date = all_days.min().date(), all_days.max().date()

with st.sidebar:
    st.markdown("### 🗓 Date Range")
    date_range = st.date_input(
        "Filter",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
        label_visibility="collapsed",
    )

if isinstance(date_range, (list, tuple)) and len(date_range) == 2:
    d_from, d_to = pd.Timestamp(date_range[0]), pd.Timestamp(date_range[1])
else:
    d_from, d_to = pd.Timestamp(min_date), pd.Timestamp(max_date)

def date_filter(df: pd.DataFrame) -> pd.DataFrame:
    return df[(df["day"] >= d_from) & (df["day"] <= d_to)]

df01 = date_filter(df01)
df02 = date_filter(df02)
df03 = date_filter(df03)
df04 = date_filter(df04)

# ── summary metrics ────────────────────────────────────────────────────────
section_divider("Summary")

c1, c2, c3, c4, c5 = st.columns(5)
with c1:
    st.metric("Transactions Created", int(df01["transactions_created"].sum()))
with c2:
    st.metric("Documents Generated", int(df02["documents_generated"].sum()))
with c3:
    st.metric("Documents Executed", int(df03["documents_executed"].sum()))
with c4:
    avg_rate = df04["execution_rate"].replace(0, pd.NA).mean()
    st.metric("Avg Execution Rate", f"{avg_rate:.0%}" if pd.notna(avg_rate) else "—")
with c5:
    peak = int(df01["transactions_created"].max())
    peak_day = df01.loc[df01["transactions_created"].idxmax(), "day"].strftime("%b %d")
    st.metric("Peak Transactions", peak, delta=f"on {peak_day}")


# ── funnel overview ────────────────────────────────────────────────────────
section_divider("Pipeline Funnel")

funnel_df = pd.DataFrame({
    "stage":  ["Transactions Created", "Documents Generated", "Documents Executed"],
    "count":  [
        int(df01["transactions_created"].sum()),
        int(df02["documents_generated"].sum()),
        int(df03["documents_executed"].sum()),
    ],
    "color": ["#6366F1", "#3B82F6", "#10B981"],
})

funnel_chart = (
    alt.Chart(funnel_df)
    .mark_bar(cornerRadiusTopRight=6, cornerRadiusBottomRight=6)
    .encode(
        y=alt.Y("stage:N", sort=None, title="", axis=alt.Axis(labelFontSize=13)),
        x=alt.X("count:Q", title="Total Count"),
        color=alt.Color("stage:N",
                        scale=alt.Scale(domain=funnel_df["stage"].tolist(),
                                        range=funnel_df["color"].tolist()),
                        legend=None),
        tooltip=[alt.Tooltip("stage:N", title="Stage"),
                 alt.Tooltip("count:Q", title="Count")],
    )
    .properties(height=160)
)

funnel_labels = (
    alt.Chart(funnel_df)
    .mark_text(align="left", dx=6, fontWeight="bold", fontSize=13)
    .encode(
        y=alt.Y("stage:N", sort=None),
        x=alt.X("count:Q"),
        text=alt.Text("count:Q"),
    )
)

st.altair_chart(funnel_chart + funnel_labels, width="stretch")


# ── daily trends (combined) ────────────────────────────────────────────────
section_divider("Daily Trends")

# Merge all three daily series for a combined line chart
trend_df = (
    df01[["day","transactions_created"]].rename(columns={"transactions_created": "value"})
    .assign(metric="Transactions Created")
    ._append(
        df02[["day","documents_generated"]].rename(columns={"documents_generated": "value"})
        .assign(metric="Documents Generated")
    )
    ._append(
        df03[["day","documents_executed"]].rename(columns={"documents_executed": "value"})
        .assign(metric="Documents Executed")
    )
)

combined_trend = (
    alt.Chart(trend_df)
    .mark_line(point=True, strokeWidth=2)
    .encode(
        x=alt.X("day:T", title="Day", axis=alt.Axis(labelAngle=0)),
        y=alt.Y("value:Q", title="Count"),
        color=alt.Color("metric:N",
                        scale=alt.Scale(
                            domain=["Transactions Created", "Documents Generated", "Documents Executed"],
                            range=["#6366F1", "#3B82F6", "#10B981"]
                        ),
                        title=""),
        tooltip=[alt.Tooltip("day:T", title="Day"),
                 alt.Tooltip("metric:N", title="Metric"),
                 alt.Tooltip("value:Q", title="Count")],
    )
    .properties(height=320)
    .interactive()
)

st.altair_chart(combined_trend, width="stretch")


# ── execution rate detail ──────────────────────────────────────────────────
section_divider("Execution Rate Detail")

kpi_header("kpi04")

base = alt.Chart(df04).encode(
    x=alt.X("day:T", title="Day", axis=alt.Axis(labelAngle=0))
)

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
    base.mark_line(point=True, color="#F59E0B", strokeWidth=2)
    .encode(
        y=alt.Y("execution_rate:Q", title="Execution Rate",
                axis=alt.Axis(orient="right", format=".0%"),
                scale=alt.Scale(domain=[0, 1])),
        tooltip=[alt.Tooltip("day:T"),
                 alt.Tooltip("execution_rate:Q", title="Rate", format=".2%")],
    )
)

rate_labels = (
    base.mark_text(align="center", dy=-12, color="#F59E0B", fontWeight="bold")
    .encode(
        y=alt.Y("execution_rate:Q", scale=alt.Scale(domain=[0, 1])),
        text=alt.Text("execution_rate:Q", format=".0%"),
    )
)

ref_rules = (
    alt.Chart(pd.DataFrame({"y": [0.5, 0.8, 1.0]}))
    .mark_rule(strokeDash=[4, 4], color="#EF4444", opacity=0.4)
    .encode(y="y:Q")
)

st.altair_chart(
    alt.layer(bars, ref_rules, rate_line, rate_labels)
    .resolve_scale(y="independent")
    .properties(height=300),
    width="stretch",
)

# ── raw data expanders ─────────────────────────────────────────────────────
section_divider("Raw Data")

with st.expander("Transactions Created"):
    st.dataframe(df01, width="stretch")
with st.expander("Documents Generated"):
    st.dataframe(df02, width="stretch")
with st.expander("Documents Executed"):
    st.dataframe(df03, width="stretch")
with st.expander("Execution Rate"):
    st.dataframe(df04, width="stretch")