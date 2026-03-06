# streamlit/pages/02_esign_engagement.py
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
from transforms import kpi05, kpi06

st.set_page_config(
    page_title="eSign & Engagement — CDP Insights",
    page_icon="✍️",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_css()
page_header("✍️ eSign & Engagement", "Parties · Funnel · Daily Events")

# ── load & transform ───────────────────────────────────────────────────────
tables = load_data()
df05 = kpi05.transform(get_table(tables, "kpi_05_parties_per_transaction"))
df06 = kpi06.transform(get_table(tables, "kpi_06_esign_funnel_events"))

# ── date filter (kpi06 only — kpi05 is per-transaction, not time-series) ──
min_date = df06["day"].min().date()
max_date = df06["day"].max().date()

with st.sidebar:
    st.markdown("### 🗓 Date Range")
    st.caption("Applies to eSign funnel (KPI 06)")
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

df06 = df06[(df06["day"] >= d_from) & (df06["day"] <= d_to)]

# ── summary metrics ────────────────────────────────────────────────────────
section_divider("Summary")

c1, c2, c3, c4, c5 = st.columns(5)
with c1:
    st.metric("Transactions", len(df05))
with c2:
    mode_parties = int(df05["distinct_parties_on_docs"].mode().iloc[0])
    st.metric("Mode: Parties / Tx", mode_parties)
with c3:
    pct_match = (df05["party_email_delta"] == 0).mean()
    st.metric("Parties == Emails", f"{pct_match:.0%}")
with c4:
    st.metric("Total eSign Events", int(df06["total_events"].sum()))
with c5:
    completed = int(df06["envelope_completed"].sum())
    sent = int(df06["envelope_sent"].sum())
    completion_rate = completed / sent if sent > 0 else 0
    st.metric("Envelope Completion Rate", f"{completion_rate:.0%}",
              delta=f"{completed} of {sent} sent")


# ══════════════════════════════════════════════════════════════════════════
# KPI 05 — Parties per Transaction
# ══════════════════════════════════════════════════════════════════════════
section_divider("KPI 05 — Parties per Transaction")
kpi_header("kpi05")

left, right = st.columns([0.55, 0.45])

with left:
    st.markdown("##### Parties on Docs vs. Signer Emails")
    max_axis = max(
        df05["distinct_parties_on_docs"].max(),
        df05["distinct_signer_emails"].max()
    )
    points = (
        alt.Chart(df05)
        .mark_circle(size=120, opacity=0.75)
        .encode(
            x=alt.X("distinct_parties_on_docs:Q", title="Distinct Parties on Documents"),
            y=alt.Y("distinct_signer_emails:Q", title="Distinct Signer Emails"),
            color=alt.Color(
                "party_email_delta:Q",
                scale=alt.Scale(scheme="blueorange", domainMid=0),
                title="Δ Parties − Emails",
            ),
            tooltip=[
                alt.Tooltip("transaction_id:N", title="Transaction ID"),
                alt.Tooltip("distinct_parties_on_docs:Q", title="Parties"),
                alt.Tooltip("distinct_signer_emails:Q", title="Signer Emails"),
                alt.Tooltip("party_email_delta:Q", title="Δ"),
            ],
        )
    )
    eq_line = (
        alt.Chart(pd.DataFrame({"x": [0, max_axis], "y": [0, max_axis]}))
        .mark_line(color="#9CA3AF", strokeDash=[6, 4])
        .encode(x="x:Q", y="y:Q")
    )
    st.altair_chart(
        alt.layer(eq_line, points).properties(height=320),
        width="stretch",
    )

with right:
    st.markdown("##### Distribution of Parties per Transaction")
    dist_df = (
        df05.groupby("distinct_parties_on_docs")
        .size()
        .reset_index(name="transactions")
    )
    dist = (
        alt.Chart(dist_df)
        .mark_bar(color="#6366F1", opacity=0.85, cornerRadiusTopLeft=4, cornerRadiusTopRight=4)
        .encode(
            x=alt.X("distinct_parties_on_docs:O", title="Distinct Parties"),
            y=alt.Y("transactions:Q", title="Transactions"),
            tooltip=[
                alt.Tooltip("distinct_parties_on_docs:O", title="Parties"),
                alt.Tooltip("transactions:Q", title="Transactions"),
            ],
        )
        .properties(height=200)
    )
    dist_labels = (
        alt.Chart(dist_df)
        .mark_text(dy=-8, fontWeight="bold", color="#6366F1")
        .encode(
            x=alt.X("distinct_parties_on_docs:O"),
            y=alt.Y("transactions:Q"),
            text=alt.Text("transactions:Q"),
        )
    )
    st.altair_chart(dist + dist_labels, width="stretch")

    # quick summary table
    st.markdown("##### Quick Stats")
    stats = pd.DataFrame({
        "Metric": ["Min Parties", "Max Parties", "Avg Parties", "Transactions with >2 Parties"],
        "Value": [
            int(df05["distinct_parties_on_docs"].min()),
            int(df05["distinct_parties_on_docs"].max()),
            f"{df05['distinct_parties_on_docs'].mean():.1f}",
            int((df05["distinct_parties_on_docs"] > 2).sum()),
        ]
    })
    st.dataframe(stats, hide_index=True, width="stretch")


# ══════════════════════════════════════════════════════════════════════════
# KPI 06 — eSign Funnel
# ══════════════════════════════════════════════════════════════════════════
section_divider("KPI 06 — eSign Funnel Events")
kpi_header("kpi06")

# ── funnel drop-off ────────────────────────────────────────────────────────
st.markdown("##### Funnel Drop-off (Period Totals)")

FUNNEL_STAGES = [
    ("envelope_sent",        "Envelope Sent",        "#6B7280"),
    ("recipient_delivered",  "Recipient Delivered",  "#6366F1"),
    ("recipient_completed",  "Recipient Completed",  "#3B82F6"),
    ("envelope_completed",   "Envelope Completed",   "#10B981"),
]

funnel_totals = [(label, int(df06[col].sum()), color)
                 for col, label, color in FUNNEL_STAGES]

funnel_df = pd.DataFrame(funnel_totals, columns=["stage", "count", "color"])
funnel_df["pct_of_sent"] = funnel_df["count"] / max(funnel_df["count"].iloc[0], 1)
funnel_df["drop_off"] = funnel_df["count"].shift(1) - funnel_df["count"]
funnel_df["drop_off"] = funnel_df["drop_off"].fillna(0).astype(int)

fa, fb = st.columns([0.6, 0.4])

with fa:
    funnel_bars = (
        alt.Chart(funnel_df)
        .mark_bar(cornerRadiusTopRight=6, cornerRadiusBottomRight=6)
        .encode(
            y=alt.Y("stage:N", sort=None, title="",
                    axis=alt.Axis(labelFontSize=13)),
            x=alt.X("count:Q", title="Total Events"),
            color=alt.Color("stage:N",
                            scale=alt.Scale(domain=funnel_df["stage"].tolist(),
                                            range=funnel_df["color"].tolist()),
                            legend=None),
            tooltip=[
                alt.Tooltip("stage:N", title="Stage"),
                alt.Tooltip("count:Q", title="Count"),
                alt.Tooltip("pct_of_sent:Q", title="% of Sent", format=".0%"),
            ],
        )
        .properties(height=180)
    )
    funnel_labels = (
        alt.Chart(funnel_df)
        .mark_text(align="left", dx=6, fontWeight="bold", fontSize=12)
        .encode(
            y=alt.Y("stage:N", sort=None),
            x="count:Q",
            text=alt.Text("count:Q"),
        )
    )
    st.altair_chart(funnel_bars + funnel_labels, width="stretch")

with fb:
    st.markdown("##### Stage Conversion")
    conv_df = funnel_df[["stage", "count", "pct_of_sent", "drop_off"]].copy()
    conv_df["pct_of_sent"] = conv_df["pct_of_sent"].map(lambda x: f"{x:.0%}")
    conv_df["drop_off"] = conv_df["drop_off"].map(lambda x: f"−{x}" if x > 0 else "—")
    conv_df.columns = ["Stage", "Count", "% of Sent", "Drop-off"]
    st.dataframe(conv_df, hide_index=True, width="stretch")

# ── daily trend ────────────────────────────────────────────────────────────
st.markdown("##### Daily eSign Events")

bar_metrics = ["envelope_sent", "recipient_delivered", "recipient_completed", "envelope_completed"]
bar_colors  = ["#6B7280", "#6366F1", "#3B82F6", "#10B981"]

base = alt.Chart(df06).encode(
    x=alt.X("day:T", title="Day", axis=alt.Axis(labelAngle=0))
)

bars = (
    base
    .transform_fold(bar_metrics, as_=["metric", "value"])
    .mark_bar(opacity=0.65)
    .encode(
        y=alt.Y("value:Q", title="Count"),
        color=alt.Color("metric:N",
                        scale=alt.Scale(domain=bar_metrics, range=bar_colors),
                        title="Event"),
        xOffset="metric:N",
        tooltip=[alt.Tooltip("day:T", title="Day"),
                 alt.Tooltip("metric:N", title="Event"),
                 alt.Tooltip("value:Q", title="Count")],
    )
)

total_line = (
    base.mark_line(point=True, color="#F59E0B", strokeWidth=2)
    .encode(
        y=alt.Y("total_events:Q", title="Total Events",
                axis=alt.Axis(orient="right")),
        tooltip=[alt.Tooltip("day:T"), alt.Tooltip("total_events:Q", title="Total")],
    )
)

st.altair_chart(
    alt.layer(bars, total_line)
    .resolve_scale(y="independent")
    .properties(height=320),
    width="stretch",
)

# ── raw data ───────────────────────────────────────────────────────────────
section_divider("Raw Data")
with st.expander("Parties per Transaction"):
    st.dataframe(df05, width="stretch")
with st.expander("eSign Funnel Events"):
    st.dataframe(df06, width="stretch")