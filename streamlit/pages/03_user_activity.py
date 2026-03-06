# streamlit/pages/03_user_activity.py
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
from transforms import kpi07, kpi09, kpi10

st.set_page_config(
    page_title="User Activity & Consent — CDP Insights",
    page_icon="👥",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_css()
page_header("👥 User Activity & Consent", "TCPA Consent · Long Realty Window · Users Updated")

# ── load & transform ───────────────────────────────────────────────────────
tables  = load_data()
df07    = kpi07.transform(get_table(tables, "kpi_07_tcpa_consent_per_day"))
df09    = kpi09.transform(get_table(tables, "kpi_09_auth_first_seen_summary"))
df10    = kpi10.transform(get_table(tables, "kpi_09_auth_users_touched_per_day"))

# ── date filter (kpi07 + kpi10) ────────────────────────────────────────────
all_days = pd.concat([df07["day"], df10["day"]])
min_date, max_date = all_days.min().date(), all_days.max().date()

with st.sidebar:
    st.markdown("### 🗓 Date Range")
    st.caption("Applies to KPI 07 & KPI 10")
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

df07 = df07[(df07["day"] >= d_from) & (df07["day"] <= d_to)]
df10 = df10[(df10["day"] >= d_from) & (df10["day"] <= d_to)]

# ── derived compliance metrics ─────────────────────────────────────────────
total_yes     = int(df07["tcpa_yes"].sum())
total_no      = int(df07["tcpa_no"].sum())
total_consent = total_yes + total_no
consent_rate  = total_yes / total_consent if total_consent > 0 else 0


# ══════════════════════════════════════════════════════════════════════════
# SUMMARY
# ══════════════════════════════════════════════════════════════════════════
section_divider("Summary")

c1, c2, c3, c4, c5 = st.columns(5)
with c1:
    st.metric("TCPA Yes (Period)", total_yes)
with c2:
    st.metric("TCPA No (Period)", total_no)
with c3:
    st.metric("Consent Rate", f"{consent_rate:.0%}",
              delta="compliant" if consent_rate >= 0.95 else "below target")
with c4:
    row09 = df09.iloc[0] if not df09.empty else None
    st.metric("Long Realty Users",
              int(row09["long_realty_users"]) if row09 is not None else "—")
with c5:
    st.metric("Users Touched (Period)", int(df10["users_touched"].sum()))


# ══════════════════════════════════════════════════════════════════════════
# KPI 07 — TCPA Consent
# ══════════════════════════════════════════════════════════════════════════
section_divider("KPI 07 — TCPA Consent")
kpi_header("kpi07")

# ── compliance score card ──────────────────────────────────────────────────
st.markdown("##### Compliance Score")

score_color = "#10B981" if consent_rate >= 0.95 else "#F59E0B" if consent_rate >= 0.80 else "#EF4444"
status_label = "Compliant ✓" if consent_rate >= 0.95 else "Watch ⚠️" if consent_rate >= 0.80 else "At Risk ✗"

sc1, sc2, sc3, sc4 = st.columns(4)
with sc1:
    st.markdown(
        f"""
        <div style="
            background: linear-gradient(135deg, {score_color}22 0%, transparent 80%);
            border: 2px solid {score_color};
            border-radius: 12px;
            padding: 1.2rem 1.4rem;
            text-align: center;
        ">
            <div style="font-size:2.2rem; font-weight:800; color:{score_color};">
                {consent_rate:.0%}
            </div>
            <div style="font-size:0.85rem; font-weight:700; color:{score_color};
                        text-transform:uppercase; letter-spacing:0.08em;">
                {status_label}
            </div>
            <div style="font-size:0.78rem; color:#6B7280; margin-top:4px;">
                TCPA Consent Rate
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with sc2:
    st.metric("Total Consent Records", total_consent)
    st.metric("Yes", total_yes)
with sc3:
    peak_day_row = df07.loc[df07["tcpa_yes"].idxmax()] if not df07.empty else None
    if peak_day_row is not None:
        st.metric("Peak Yes Day", peak_day_row["day"].strftime("%b %d"),
                  delta=f"{int(peak_day_row['tcpa_yes'])} consents")
with sc4:
    active_days = int((df07["total_records"] > 0).sum())
    st.metric("Active Consent Days", active_days)
    avg_daily = df07[df07["total_records"] > 0]["total_records"].mean()
    st.metric("Avg Records / Active Day", f"{avg_daily:.1f}")

st.markdown("<br>", unsafe_allow_html=True)

# ── consent trend ──────────────────────────────────────────────────────────
st.markdown("##### Daily Consent Trend")

base07 = alt.Chart(df07).encode(
    x=alt.X("day:T", title="Day", axis=alt.Axis(labelAngle=0))
)

consent_bars = (
    base07
    .transform_fold(["tcpa_yes", "tcpa_no"], as_=["metric", "value"])
    .mark_bar(opacity=0.75)
    .encode(
        y=alt.Y("value:Q", title="Count"),
        color=alt.Color("metric:N",
                        scale=alt.Scale(domain=["tcpa_yes", "tcpa_no"],
                                        range=["#10B981", "#EF4444"]),
                        title="Consent"),
        xOffset="metric:N",
        tooltip=[alt.Tooltip("day:T", title="Day"),
                 alt.Tooltip("metric:N", title="Type"),
                 alt.Tooltip("value:Q", title="Count")],
    )
)

total_line = (
    base07.mark_line(point=True, color="#2563EB", strokeWidth=2)
    .encode(
        y=alt.Y("total_records:Q", title="Total Records",
                axis=alt.Axis(orient="right")),
        tooltip=[alt.Tooltip("day:T"), alt.Tooltip("total_records:Q", title="Total")],
    )
)

st.altair_chart(
    alt.layer(consent_bars, total_line)
    .resolve_scale(y="independent")
    .properties(height=300),
    width="stretch",
)


# ══════════════════════════════════════════════════════════════════════════
# KPI 09 + KPI 10 — Long Realty Window & Users Touched
# ══════════════════════════════════════════════════════════════════════════
section_divider("KPI 09 & 10 — Long Realty Users")

left, right = st.columns([0.48, 0.52])

# ── left: KPI 09 timeline ──────────────────────────────────────────────────
with left:
    kpi_header("kpi09")

    if df09.empty or df09["first_seen_ts"].isna().all():
        st.warning("No KPI 09 data available.")
    else:
        row = df09.iloc[0]

        m1, m2, m3 = st.columns(3)
        with m1:
            st.metric("Long Realty Users", int(row["long_realty_users"]))
        with m2:
            st.metric("First Seen (UTC)", row["first_seen_ts"].strftime("%b %d, %Y"))
        with m3:
            st.metric("Last Seen (UTC)", row["last_seen_ts"].strftime("%b %d, %Y"))

        span_days = float(row["span_days"])
        total_minutes = int(round(span_days * 24 * 60))
        d, rem   = divmod(total_minutes, 24 * 60)
        hh, mm   = divmod(rem, 60)
        span_fmt = f"{d} days, {hh:02d}:{mm:02d}" if d > 0 else f"{hh:02d}:{mm:02d}"
        st.metric("Active Window Span", span_fmt)

        st.markdown("##### Activity Window Timeline")
        timeline_df = pd.DataFrame({
            "label": ["Active Window"],
            "start": [pd.to_datetime(row["first_seen_ts"])],
            "end":   [pd.to_datetime(row["last_seen_ts"])],
        })

        bar = (
            alt.Chart(timeline_df)
            .mark_bar(height=28, cornerRadius=8, color="#14B8A6")
            .encode(
                x=alt.X("start:T", title=""),
                x2="end:T",
                y=alt.Y("label:N", title=""),
            )
            .properties(height=80)
        )
        ticks = (
            alt.Chart(timeline_df)
            .transform_fold(["start", "end"], as_=["kind", "time"])
            .mark_tick(thickness=2, size=28, color="#0F766E")
            .encode(
                x="time:T",
                y="label:N",
                tooltip=[alt.Tooltip("kind:N", title="Edge"),
                         alt.Tooltip("time:T", title="Timestamp (UTC)")],
            )
        )
        st.altair_chart(bar + ticks, width="stretch")

        with st.expander("Show raw KPI 09 data"):
            st.dataframe(
                df09[["first_seen_ts", "last_seen_ts", "long_realty_users",
                       "span_hours", "span_days"]],
                width="stretch",
            )

# ── right: KPI 10 users touched ────────────────────────────────────────────
with right:
    kpi_header("kpi10")

    r1, r2, r3 = st.columns(3)
    with r1:
        st.metric("Total Users Touched", int(df10["users_touched"].sum()))
    with r2:
        st.metric("Avg / Day", f"{df10['users_touched'].mean():.1f}")
    with r3:
        peak_val = int(df10["users_touched"].max())
        peak_dt  = df10.loc[df10["users_touched"].idxmax(), "day"].strftime("%b %d")
        st.metric("Peak Day", peak_val, delta=peak_dt)

    st.markdown("##### Daily Users Touched")
    base10 = alt.Chart(df10).encode(
        x=alt.X("day:T", title="Day", axis=alt.Axis(labelAngle=0))
    )

    daily = (
        base10.mark_bar(color="#0EA5E9", opacity=0.7,
                        cornerRadiusTopLeft=3, cornerRadiusTopRight=3)
        .encode(
            y=alt.Y("users_touched:Q", title="Users Touched"),
            tooltip=[alt.Tooltip("day:T", title="Day"),
                     alt.Tooltip("users_touched:Q", title="Users")],
        )
    )

    rolling = (
        base10.mark_line(color="#6366F1", strokeWidth=2, strokeDash=[4, 2])
        .encode(
            y=alt.Y("7d_rolling:Q"),
            tooltip=[alt.Tooltip("day:T"),
                     alt.Tooltip("7d_rolling:Q", title="7-day Avg", format=".1f")],
        )
    )

    st.altair_chart(
        alt.layer(daily, rolling).properties(height=300),
        width="stretch",
    )

    with st.expander("Show raw KPI 10 data"):
        st.dataframe(df10, width="stretch")


# ── raw data ───────────────────────────────────────────────────────────────
section_divider("Raw Data")
with st.expander("TCPA Consent (KPI 07)"):
    st.dataframe(df07, width="stretch")