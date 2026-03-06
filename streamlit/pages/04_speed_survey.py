# streamlit/pages/04_speed_survey.py
from __future__ import annotations

import sys
from pathlib import Path

import altair as alt
import numpy as np
import pandas as pd
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))  # apps/
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))          # streamlit/

from utils.dashboard_utils import (
    inject_css, load_data, get_table,
    kpi_header, page_header, section_divider,
)
from transforms import kpi08, kpi11

st.set_page_config(
    page_title="Speed & Survey — CDP Insights",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_css()
page_header("⚡ Speed & Survey", "Time to Execution · PHM Survey Outcomes")

# ── load & transform ───────────────────────────────────────────────────────
tables = load_data()
df08   = kpi08.transform(get_table(tables, "kpi_08_time_to_transaction_execution"))
df11   = kpi11.transform(get_table(tables, "kpi_10_phm_survey_question_counts"))

# ── helpers ────────────────────────────────────────────────────────────────
def fmt_mmss(seconds: float) -> str:
    m = int(seconds // 60)
    s = seconds - m * 60
    return f"{m}:{s:04.1f}"


# ══════════════════════════════════════════════════════════════════════════
# SUMMARY
# ══════════════════════════════════════════════════════════════════════════
section_divider("Summary")

row08 = df08.iloc[0] if not df08.empty else None

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.metric("Executed Transactions",
              int(row08["executed_transactions"]) if row08 is not None else "—")
with c2:
    st.metric("Median Time to Execution",
              fmt_mmss(row08["median_seconds"]) if row08 is not None else "—")
with c3:
    st.metric("P95 Time to Execution",
              fmt_mmss(row08["p95_seconds"]) if row08 is not None else "—")
with c4:
    total_survey = int(df11[["true_count", "false_count", "missing_count"]].sum().sum())
    st.metric("Total Survey Responses", total_survey)


# ══════════════════════════════════════════════════════════════════════════
# KPI 08 — Time to Execution
# ══════════════════════════════════════════════════════════════════════════
section_divider("KPI 08 — Time to Execution")
kpi_header("kpi08")

if row08 is None:
    st.warning("No KPI 08 data available.")
else:
    median_s  = float(row08["median_seconds"])
    p95_s     = float(row08["p95_seconds"])
    median_m  = float(row08["median_minutes"])
    p95_m     = float(row08["p95_minutes"])

    # ── sidebar: target threshold ──────────────────────────────────────────
    with st.sidebar:
        st.markdown("### ⚡ Execution Target")
        target_min = st.slider(
            "Target P95 (minutes)", min_value=1, max_value=60,
            value=15, step=1,
        )
        target_s = target_min * 60

    # ── gauge row ──────────────────────────────────────────────────────────
    st.markdown("##### P95 vs Target Threshold")

    p95_pct    = min(p95_s / target_s, 1.5)   # cap at 150% for display
    gauge_color = "#10B981" if p95_s <= target_s else "#EF4444"
    gauge_label = "Within Target ✓" if p95_s <= target_s else "Exceeds Target ✗"

    g1, g2, g3 = st.columns([0.3, 0.4, 0.3])
    with g2:
        # SVG arc gauge
        pct_capped = min(p95_pct, 1.0)
        sweep      = pct_capped * 180          # degrees (half circle)
        rad        = sweep * np.pi / 180
        end_x      = 150 - 110 * np.cos(rad)
        end_y      = 130 - 110 * np.sin(rad)
        large_arc  = 1 if sweep > 180 else 0

        st.markdown(
            f"""
            <div style="text-align:center;">
              <svg viewBox="0 0 300 160" width="100%" style="max-width:320px;">
                <!-- background arc -->
                <path d="M 40 130 A 110 110 0 0 1 260 130"
                      fill="none" stroke="#E5E7EB" stroke-width="22"
                      stroke-linecap="round"/>
                <!-- value arc -->
                <path d="M 40 130 A 110 110 0 {large_arc} 1 {end_x:.1f} {end_y:.1f}"
                      fill="none" stroke="{gauge_color}" stroke-width="22"
                      stroke-linecap="round"/>
                <!-- target tick at 100% -->
                <line x1="150" y1="22" x2="150" y2="46"
                      stroke="#6B7280" stroke-width="3" stroke-dasharray="4,2"/>
                <!-- center label -->
                <text x="150" y="108" text-anchor="middle"
                      font-size="28" font-weight="800" fill="{gauge_color}">
                  {fmt_mmss(p95_s)}
                </text>
                <text x="150" y="132" text-anchor="middle"
                      font-size="12" fill="#6B7280">P95 Execution Time</text>
                <text x="150" y="150" text-anchor="middle"
                      font-size="11" font-weight="700" fill="{gauge_color}">
                  {gauge_label}
                </text>
                <!-- axis labels -->
                <text x="36" y="150" text-anchor="middle"
                      font-size="10" fill="#9CA3AF">0</text>
                <text x="264" y="150" text-anchor="middle"
                      font-size="10" fill="#9CA3AF">Target: {target_min}m</text>
              </svg>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── bar comparison ─────────────────────────────────────────────────────
    st.markdown("##### Median vs P95 Comparison")

    chart_df = pd.DataFrame({
        "metric":  ["Median", "P95"],
        "minutes": [median_m, p95_m],
        "seconds": [median_s, p95_s],
        "label":   [fmt_mmss(median_s), fmt_mmss(p95_s)],
    })
    scale_max = max(p95_m, target_min) * 1.2

    bars = (
        alt.Chart(chart_df)
        .mark_bar(cornerRadiusTopRight=6, cornerRadiusBottomRight=6)
        .encode(
            x=alt.X("minutes:Q", title="Minutes",
                    scale=alt.Scale(domain=[0, scale_max])),
            y=alt.Y("metric:N", title="", sort=["P95", "Median"],
                    axis=alt.Axis(labelFontSize=13)),
            color=alt.Color("metric:N",
                            scale=alt.Scale(domain=["Median", "P95"],
                                            range=["#10B981", gauge_color]),
                            legend=None),
            tooltip=[alt.Tooltip("metric:N"),
                     alt.Tooltip("minutes:Q", format=".1f", title="Minutes"),
                     alt.Tooltip("label:N", title="mm:ss")],
        )
        .properties(height=140)
    )

    bar_labels = (
        alt.Chart(chart_df)
        .mark_text(align="left", dx=6, fontWeight="bold", fontSize=13)
        .encode(
            x=alt.X("minutes:Q", scale=alt.Scale(domain=[0, scale_max])),
            y=alt.Y("metric:N", sort=["P95", "Median"]),
            text="label:N",
            color=alt.Color("metric:N",
                            scale=alt.Scale(domain=["Median", "P95"],
                                            range=["#10B981", gauge_color]),
                            legend=None),
        )
    )

    target_rule = (
        alt.Chart(pd.DataFrame({"x": [target_min]}))
        .mark_rule(color="#6B7280", strokeDash=[5, 3], strokeWidth=2)
        .encode(x="x:Q")
    )
    target_label = (
        alt.Chart(pd.DataFrame({"x": [target_min], "y": ["P95"], "t": [f"Target: {target_min}m"]}))
        .mark_text(align="left", dx=4, dy=-14, color="#6B7280", fontSize=11)
        .encode(x="x:Q", y=alt.Y("y:N", sort=["P95", "Median"]), text="t:N")
    )

    st.altair_chart(
        alt.layer(bars, bar_labels, target_rule, target_label)
        .properties(height=140),
        width="stretch",
    )


# ══════════════════════════════════════════════════════════════════════════
# KPI 11 — PHM Survey Heatmap
# ══════════════════════════════════════════════════════════════════════════
section_divider("KPI 11 — PHM Survey Question Counts")
kpi_header("kpi11")

if df11.empty:
    st.warning("No KPI 11 data available.")
else:
    # ── heatmap: metric × date, color = true ratio ─────────────────────────
    st.markdown("##### True Response Rate — Metric × Date")
    st.caption("Color intensity = true / (true + false + missing). White = no data.")

    heat_df = df11.copy()
    heat_df["total"]      = heat_df["true_count"] + heat_df["false_count"] + heat_df["missing_count"]
    heat_df["true_ratio"] = heat_df["true_count"] / heat_df["total"].replace(0, pd.NA)
    heat_df["date_str"]   = heat_df["event_date"].dt.strftime("%b %d")
    heat_df["true_ratio"] = heat_df["true_ratio"].fillna(0.0)

    heatmap = (
        alt.Chart(heat_df)
        .mark_rect(cornerRadius=4)
        .encode(
            x=alt.X("date_str:O",
                    sort=heat_df.sort_values("event_date")["date_str"].unique().tolist(),
                    title="Date",
                    axis=alt.Axis(labelAngle=-30)),
            y=alt.Y("metric:N", title="Survey Question",
                    axis=alt.Axis(labelFontSize=12)),
            color=alt.Color(
                "true_ratio:Q",
                scale=alt.Scale(scheme="greens", domain=[0, 1]),
                title="True Rate",
                legend=alt.Legend(format=".0%"),
            ),
            tooltip=[
                alt.Tooltip("metric:N", title="Question"),
                alt.Tooltip("date_str:O", title="Date"),
                alt.Tooltip("true_ratio:Q", title="True Rate", format=".0%"),
                alt.Tooltip("true_count:Q", title="True"),
                alt.Tooltip("false_count:Q", title="False"),
                alt.Tooltip("missing_count:Q", title="Missing"),
            ],
        )
        .properties(height=180)
    )

    heatmap_text = (
        alt.Chart(heat_df)
        .mark_text(fontSize=11, fontWeight="bold")
        .encode(
            x=alt.X("date_str:O",
                    sort=heat_df.sort_values("event_date")["date_str"].unique().tolist()),
            y=alt.Y("metric:N"),
            text=alt.Text("true_ratio:Q", format=".0%"),
            color=alt.condition(
                alt.datum.true_ratio > 0.55,
                alt.value("white"),
                alt.value("#374151"),
            ),
        )
    )

    st.altair_chart(heatmap + heatmap_text, width="stretch")

    # ── stacked totals per question ────────────────────────────────────────
    st.markdown("##### Response Totals per Question")

    totals_df = (
        df11.groupby("metric")[["true_count", "false_count", "missing_count"]]
        .sum()
        .reset_index()
        .melt(id_vars="metric", var_name="outcome", value_name="count")
    )

    stacked = (
        alt.Chart(totals_df)
        .mark_bar(cornerRadiusTopRight=4, cornerRadiusBottomRight=4)
        .encode(
            y=alt.Y("metric:N", title="", axis=alt.Axis(labelFontSize=12)),
            x=alt.X("count:Q", title="Total Responses"),
            color=alt.Color(
                "outcome:N",
                scale=alt.Scale(
                    domain=["true_count", "false_count", "missing_count"],
                    range=["#10B981", "#EF4444", "#9CA3AF"],
                ),
                title="Outcome",
            ),
            order=alt.Order("outcome:N", sort="ascending"),
            tooltip=[
                alt.Tooltip("metric:N", title="Question"),
                alt.Tooltip("outcome:N", title="Outcome"),
                alt.Tooltip("count:Q", title="Count"),
            ],
        )
        .properties(height=160)
    )

    st.altair_chart(stacked, width="stretch")

    # ── per-metric detail tabs ─────────────────────────────────────────────
    st.markdown("##### Per-Question Detail")
    metrics = sorted(df11["metric"].unique().tolist())

    for metric_name, tab in zip(metrics, st.tabs(metrics)):
        with tab:
            mdf = df11[df11["metric"] == metric_name].copy()
            if not mdf["event_date"].isna().all():
                mdf = (mdf.sort_values("event_date")
                          .set_index("event_date")
                          .reindex(pd.date_range(mdf["event_date"].min(),
                                                 mdf["event_date"].max(), freq="D"))
                          .rename_axis("event_date").reset_index())
                mdf["metric"] = mdf["metric"].fillna(metric_name)
                for col in ["true_count", "false_count", "missing_count"]:
                    mdf[col] = mdf[col].fillna(0.0)

            t1, t2, t3, t4 = st.columns(4)
            with t1: st.metric("True (Σ)",    int(mdf["true_count"].sum()))
            with t2: st.metric("False (Σ)",   int(mdf["false_count"].sum()))
            with t3: st.metric("Missing (Σ)", int(mdf["missing_count"].sum()))
            with t4:
                tot = mdf["true_count"].sum() + mdf["false_count"].sum()
                rate = mdf["true_count"].sum() / tot if tot > 0 else 0
                st.metric("True Rate", f"{rate:.0%}")

            with st.expander("Show data", expanded=False):
                st.dataframe(mdf, width="stretch")

    # ── raw data ───────────────────────────────────────────────────────────
    section_divider("Raw Data")
    with st.expander("PHM Survey (KPI 11)"):
        st.dataframe(df11, width="stretch")