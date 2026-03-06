import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime

# -------------------- Page configuration --------------------
st.set_page_config(
    page_title="CDP Insights",
    page_icon="assets/favicon.png",   # keep or change to "📊" if no image yet
    layout="wide",
    initial_sidebar_state="expanded",
)

# -------------------- Light CSS polish ----------------------
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

# -------------------- Header -------------------------------
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

# -------------------- Sidebar Navigation -------------------
# def sidebar():
#     st.sidebar.title("Navigation")
#     return st.sidebar.radio(
#         "Go to",
#         options=[
#             "Overview",
#             "KPI 01 – Transactions Created",
#             "KPI 02 – Documents Generated",  # adding kpi 2 to the sidebar options
#             "KPI 03 – Documents Executed",
#             "KPI 04 – Daily Execution Rate",
#             "KPI 05 – Parties per Transaction",
#             "KPI 06 – Envelope & Recipient Events",
#             "KPI 07 – TCPA Consent",
#             "KPI 08 – Time to Txn Execution",
#         ],
#         index=0,
#         label_visibility="collapsed",
#     )

# -------------------- Sidebar Navigation (unified) -------------------
def sidebar():
    st.sidebar.title("Navigation")

    # Use a single source of truth for page labels and handlers
    PAGES = {
        "Overview": overview_section,
        "KPI 01 – Transactions Created": kpi01_section,
        "KPI 02 – Documents Generated": kpi02_section,
        "KPI 03 – Documents Executed": kpi03_section,
        "KPI 04 – Daily Execution Rate": kpi04_section,
        "KPI 05 – Parties per Transaction": kpi05_section,
        "KPI 06 – Envelope & Recipient Events": kpi06_section,
        "KPI 07 – TCPA Consent": kpi07_section,
        "KPI 08 – Time to Txn Execution": kpi08_section,  # added KPI 08 to the pages dictionary
        "KPI 09 – Long Realty Users Window": kpi09_section,
        "KPI 10 – Users Touched (Daily)": kpi10_section,
        "KPI 11 – Boolean Outcomes (Daily)": kpi11_section,
    }

    selected = st.sidebar.radio("Go to", options=list(PAGES.keys()), index=0, label_visibility="collapsed")
    return selected, PAGES[selected]



# -------------------- KPI 01 Data & Chart ------------------
PASTED_DATA = """day\ttransactions_created
2/18/2026\t2
2/19/2026\t2
2/21/2026\t7
2/23/2026\t2
2/24/2026\t1
2/25/2026\t1
2/26/2026\t1
2/27/2026\t1
2/28/2026\t9
"""


# -------------------- KPI 02 Data (pasted) ------------------
PASTED_DATA_KPI2 = """day\tdocuments_generated
2/18/2026\t2
2/19/2026\t2
2/21/2026\t7
2/23/2026\t2
2/24/2026\t1
2/25/2026\t1
2/26/2026\t1
2/27/2026\t1
"""


# -------------------- KPI 03 Data (pasted) ------------------
PASTED_DATA_KPI3 = """day\tdocuments_executed
2/18/2026\t1
2/19/2026\t1
2/22/2026\t1
2/23/2026\t1
2/24/2026\t1
"""

# -------------------- KPI 04 Data (pasted) ------------------
PASTED_DATA_KPI4 = """day\tgenerated\texecuted\texecution_rate
2/18/2026\t2\t1\t0.5
2/19/2026\t2\t1\t0.5
2/21/2026\t7\t0\t0.00E+00
2/23/2026\t2\t1\t0.5
2/24/2026\t1\t1\t1
2/25/2026\t1\t0\t0.00E+00
2/26/2026\t1\t0\t0.00E+00
2/27/2026\t1\t0\t0.00E+00
"""

# -------------------- KPI 05 Data (pasted) ------------------
PASTED_DATA_KPI5 = """transaction_id\tdistinct_parties_on_docs\tdistinct_signer_emails
019c6ea7-ed80-7d1e-acb6-42c279830bd6\t3\t3
019c7324-1293-7df0-b18d-fc34389efcf3\t2\t2
019c7347-e80f-73b4-8276-b72013d7cfaa\t2\t2
019c7757-deb5-7b0b-b5a1-c00ca12907a8\t2\t2
019c7d81-ab7d-77af-aff7-68a5f25508b2\t2\t2
019c7e30-d0d8-7214-979c-3ad6f093db05\t2\t2
019c7e3f-bf56-7f9e-81a7-389a149b9adc\t2\t2
019c80ca-9398-7be4-a30a-746d00aaaa7c\t2\t2
019c826f-3b61-7d25-85aa-9bce7909c341\t2\t2
019c8272-1fd6-7bec-9fab-6eb546848684\t2\t2
019c8275-a6e7-7894-895b-187b38dcc63b\t2\t2
019c8c82-02bc-78ec-a1dc-2c9df1a98160\t2\t2
019c8cd4-6422-7a75-92b6-b778169e42bd\t2\t2
019c8cfa-f121-751d-b91a-67f07104806b\t2\t2
019c95e4-7a54-775c-b0ae-beffe26001b1\t2\t2
019c9ab4-aecc-7eb6-ad43-06c2f514084d\t2\t2
019ca186-7c53-7544-92c3-06fa16d27988\t3\t3
019ca758-0c08-7976-8dc0-d1ebce57a252\t2\t2
"""
# -------------------- KPI 06 Data (pasted) ------------------
PASTED_DATA_KPI6 = """day\tenvelope_sent\trecipient_delivered\trecipient_completed\tenvelope_completed\ttotal_events
2/18/2026\t4\t5\t8\t1\t22
2/19/2026\t4\t4\t6\t1\t19
2/21/2026\t14\t9\t10\t0\t37
2/22/2026\t0\t1\t2\t1\t6
2/23/2026\t4\t3\t4\t1\t14
2/24/2026\t2\t2\t4\t1\t11
2/25/2026\t2\t1\t2\t0\t5
2/26/2026\t2\t1\t0\t0\t3
2/27/2026\t2\t1\t2\t0\t5
"""
# -------------------- KPI 07 Data (pasted) ------------------
PASTED_DATA_KPI7 = """day\ttcpa_yes\ttcpa_no\ttotal_records
2/6/2026\t1\t0\t1
2/10/2026\t1\t0\t1
2/12/2026\t3\t0\t3
2/13/2026\t1\t0\t1
2/17/2026\t2\t0\t2
2/18/2026\t8\t0\t8
2/19/2026\t7\t0\t7
2/20/2026\t2\t0\t2
2/21/2026\t4\t0\t4
2/22/2026\t1\t0\t1
2/23/2026\t3\t0\t3
2/25/2026\t3\t0\t3
2/26/2026\t1\t0\t1
2/27/2026\t1\t0\t1
2/28/2026\t2\t0\t2
"""

# -------------------- KPI 08 Data (pasted) ------------------
PASTED_DATA_KPI8 = """executed_transactions\tmedian_time_to_txn_execution\tp95_time_to_txn_execution
5\t07:58.8\t11:30.0
"""

# -------------------- KPI 09 Data (pasted) ------------------
PASTED_DATA_KPI9 = """first_seen_ts\tlast_seen_ts\tlong_realty_users
2026-02-13 05:14:47.929035+00:00\t2026-02-27 23:01:00.270488+00:00\t84
"""

# -------------------- KPI 10 Data (pasted) ------------------
PASTED_DATA_KPI10 = """day\tusers_touched
2/13/2026\t42
2/18/2026\t9
2/19/2026\t5
2/20/2026\t1
2/21/2026\t7
2/23/2026\t2
2/24/2026\t9
2/25/2026\t3
2/26/2026\t2
2/27/2026\t4
"""

# -------------------- KPI 11 Data (pasted) ------------------
PASTED_DATA_KPI11 = """event_date\tmetric\ttrue_count\tfalse_count\tmissing_count
3/1/2026\thasExistingMortgageCompany\t1\t0\t0
3/1/2026\tinterestedInLowerPayment\t0\t0\t1
2/23/2026\thasExistingMortgageCompany\t0\t1\t0
2/23/2026\tinterestedInLowerPayment\t1\t0\t0
2/19/2026\thasExistingMortgageCompany\t0\t1\t0
2/19/2026\tinterestedInLowerPayment\t1\t0\t0
2/18/2026\thasExistingMortgageCompany\t1\t0\t0
2/18/2026\tinterestedInLowerPayment\t1\t0\t0
"""









def load_kpi01_df(text: str) -> pd.DataFrame:
    # Read the pasted tab-separated text
    from io import StringIO
    df = pd.read_csv(StringIO(text), sep=r"\t", engine="python")

    # Parse dates and clean numeric column (handles stray characters like "1.")
    df["day"] = pd.to_datetime(df["day"])
    df["transactions_created"] = (
        pd.to_numeric(df["transactions_created"].astype(str).str.extract(r"([0-9]+\.?[0-9]*)")[0],
                      errors="coerce")
        .fillna(0)
        .astype(float)
    )

    # Sort and ensure a continuous date index (fill missing days with 0)
    df = df.sort_values("day").set_index("day")
    full_index = pd.date_range(df.index.min(), df.index.max(), freq="D")
    df = df.reindex(full_index).fillna(0.0).rename_axis("day").reset_index()

    return df

def kpi01_section():
    st.subheader("KPI 01 – Transactions Created (Daily)")
    df = load_kpi01_df(PASTED_DATA)

    # Show the data quickly
    with st.expander("Show data", expanded=False):
        st.dataframe(df, use_container_width=True)

    # Altair time-series line + points + tooltip
    chart = (
        alt.Chart(df)
        .mark_line(point=True)
        .encode(
            x=alt.X("day:T", title="Day"),
            y=alt.Y("transactions_created:Q", title="Transactions Created"),
            tooltip=[
                alt.Tooltip("day:T", title="Day"),
                alt.Tooltip("transactions_created:Q", title="Transactions"),
            ],
        )
        .properties(height=320)
        .interactive()
    )
    st.altair_chart(chart, use_container_width=True)

def load_kpi02_df(text: str) -> pd.DataFrame:
    from io import StringIO
    df = pd.read_csv(StringIO(text), sep=r"\t", engine="python")
    df["day"] = pd.to_datetime(df["day"])

    # Clean numeric text (handles stray "1." etc.)
    df["documents_generated"] = (
        pd.to_numeric(df["documents_generated"].astype(str).str.extract(r"([0-9]+\.?[0-9]*)")[0],
                      errors="coerce")
        .fillna(0)
        .astype(float)
    )

    # Sort and fill missing days (0)
    df = df.sort_values("day").set_index("day")
    full_index = pd.date_range(df.index.min(), df.index.max(), freq="D")
    df = df.reindex(full_index).fillna(0.0).rename_axis("day").reset_index()
    return df

def kpi02_section():
    st.subheader("KPI 02 – Documents Generated (Daily)")
    df = load_kpi02_df(PASTED_DATA_KPI2)

    with st.expander("Show data", expanded=False):
        st.dataframe(df, use_container_width=True)

    chart = (
        alt.Chart(df)
        .mark_line(point=True)
        .encode(
            x=alt.X("day:T", title="Day"),
            y=alt.Y("documents_generated:Q", title="Documents Generated"),
            tooltip=[
                alt.Tooltip("day:T", title="Day"),
                alt.Tooltip("documents_generated:Q", title="Documents"),
            ],
        )
        .properties(height=320)
        .interactive()
    )
    st.altair_chart(chart, use_container_width=True)


def load_kpi03_df(text: str) -> pd.DataFrame:
    from io import StringIO
    df = pd.read_csv(StringIO(text), sep=r"\t", engine="python")
    df["day"] = pd.to_datetime(df["day"])

    # Clean numeric text in case of stray characters (e.g., "1.")
    df["documents_executed"] = (
        pd.to_numeric(df["documents_executed"].astype(str).str.extract(r"([0-9]+\.?[0-9]*)")[0],
                      errors="coerce")
        .fillna(0)
        .astype(float)
    )

    # Sort and fill missing days with 0 so the line connects across the date range
    df = df.sort_values("day").set_index("day")
    full_index = pd.date_range(df.index.min(), df.index.max(), freq="D")
    df = df.reindex(full_index).fillna(0.0).rename_axis("day").reset_index()
    return df

def kpi03_section():
    st.subheader("KPI 03 – Documents Executed (Daily)")
    df = load_kpi03_df(PASTED_DATA_KPI3)

    with st.expander("Show data", expanded=False):
        st.dataframe(df, use_container_width=True)

    chart = (
        alt.Chart(df)
        .mark_line(point=True)
        .encode(
            x=alt.X("day:T", title="Day"),
            y=alt.Y("documents_executed:Q", title="Documents Executed"),
            tooltip=[
                alt.Tooltip("day:T", title="Day"),
                alt.Tooltip("documents_executed:Q", title="Documents"),
            ],
        )
        .properties(height=320)
        .interactive()
    )
    st.altair_chart(chart, use_container_width=True)


def load_kpi04_df(text: str) -> pd.DataFrame:
    from io import StringIO
    df = pd.read_csv(StringIO(text), sep=r"\t", engine="python")

    # Parse date
    df["day"] = pd.to_datetime(df["day"])

    # Clean numeric columns:
    # - allow integers/floats
    # - handle Excel-like scientific notation (e.g., 0.00E+00)
    for col in ["generated", "executed", "execution_rate"]:
        # Extract a valid number (supports integers, decimals, scientific notation)
        df[col] = pd.to_numeric(
            df[col].astype(str).str.extract(r"([+-]?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?)")[0],
            errors="coerce"
        ).fillna(0.0)

    # If execution_rate is missing or zero where generated>0, recompute as executed/generated
    # (keeps provided values otherwise)
    needs_calc = (df["generated"] > 0) & (df["execution_rate"] == 0)
    df.loc[needs_calc, "execution_rate"] = df.loc[needs_calc, "executed"] / df.loc[needs_calc, "generated"]

    # Clip to [0,1] just in case
    df["execution_rate"] = df["execution_rate"].clip(0, 1)

    # Sort and fill missing days with zeros so the line connects across the full range
    df = df.sort_values("day").set_index("day")
    full_index = pd.date_range(df.index.min(), df.index.max(), freq="D")
    df = df.reindex(full_index).fillna(0.0).rename_axis("day").reset_index()

    return df

def kpi04_section():
    st.subheader("KPI 04 – Daily Execution Rate (Generated vs Executed + Rate)")

    df = load_kpi04_df(PASTED_DATA_KPI4)

    with st.expander("Show data", expanded=False):
        st.dataframe(df, use_container_width=True)

    # ---------- Base (shared x) ----------
    base = alt.Chart(df).encode(
        x=alt.X("day:T", title="Day", axis=alt.Axis(labelAngle=0))
    )

    # ---------- Grouped bars: Generated vs Executed (left axis) ----------
    bars = (
        base
        .transform_fold(["generated", "executed"], as_=["metric", "value"])
        .mark_bar(opacity=0.5)
        .encode(
            y=alt.Y("value:Q", title="Count"),
            color=alt.Color(
                "metric:N",
                scale=alt.Scale(
                    domain=["generated", "executed"],
                    range=["#9CA3AF", "#10B981"]  # gray, green
                ),
                title=""
            ),
            xOffset="metric:N",  # side-by-side bars (Altair 5+)
            tooltip=[
                alt.Tooltip("day:T", title="Day"),
                alt.Tooltip("metric:N", title="Metric"),
                alt.Tooltip("value:Q", title="Count"),
            ],
        )
    )

    # ---------- Line + points: Execution Rate (right axis, 0..1) ----------
    rate_line = (
        base
        .mark_line(point=True, color="#2563EB")
        .encode(
            y=alt.Y(
                "execution_rate:Q",
                title="Execution Rate",
                axis=alt.Axis(orient="right", format=".0%"),
                scale=alt.Scale(domain=[0, 1])
            ),
            tooltip=[
                alt.Tooltip("day:T", title="Day"),
                alt.Tooltip("execution_rate:Q", title="Rate", format=".2%")
            ],
        )
    )

    # Optional: percent labels above points
    rate_labels = (
        base
        .mark_text(align="center", dy=-10, color="#2563EB")
        .encode(
            y=alt.Y("execution_rate:Q", scale=alt.Scale(domain=[0, 1])),
            text=alt.Text("execution_rate:Q", format=".0%")
        )
    )

    # ---------- Reference lines at 50%, 80%, 100% ----------
    thresholds = pd.DataFrame({"y": [0.5, 0.8, 1.0]})
    ref_rules = (
        alt.Chart(thresholds)
        .mark_rule(strokeDash=[4, 4], color="#EF4444")
        .encode(y=alt.Y("y:Q"))
    )

    # ---------- Combine (single shared height here) ----------
    combined = (
        alt.layer(
            bars,
            ref_rules,
            rate_line,
            rate_labels
        )
        .resolve_scale(y="independent")   # bars on left, rate on right
        .properties(height=280)           # set height ONCE for the whole layer
    )

    st.altair_chart(combined, use_container_width=True)


def load_kpi05_df(text: str) -> pd.DataFrame:
    from io import StringIO
    df = pd.read_csv(StringIO(text), sep=r"\t", engine="python")
    # Ensure numeric types (in case values were pasted as strings)
    for col in ["distinct_parties_on_docs", "distinct_signer_emails"]:
        df[col] = pd.to_numeric(
            df[col].astype(str).str.extract(r"([+-]?\d+(?:\.\d+)?)")[0],
            errors="coerce"
        ).fillna(0).astype(int)
    # Helper: difference (positive = more parties than signer emails)
    df["party_email_delta"] = df["distinct_parties_on_docs"] - df["distinct_signer_emails"]
    return df

def kpi05_section():
    st.subheader("KPI 05 – Parties per Transaction")

    df = load_kpi05_df(PASTED_DATA_KPI5)

    with st.expander("Show data", expanded=False):
        st.dataframe(df, use_container_width=True)

    st.markdown("#### Relationship: Parties on Docs vs. Signer Emails")
    # Scatter with equality line y = x
    scatter_base = alt.Chart(df).encode(
        x=alt.X("distinct_parties_on_docs:Q", title="Distinct Parties on Documents"),
        y=alt.Y("distinct_signer_emails:Q", title="Distinct Signer Emails"),
        tooltip=[
            alt.Tooltip("transaction_id:N", title="Transaction ID"),
            alt.Tooltip("distinct_parties_on_docs:Q", title="Parties"),
            alt.Tooltip("distinct_signer_emails:Q", title="Signer Emails"),
            alt.Tooltip("party_email_delta:Q", title="Δ (Parties - Emails)"),
        ],
    )

    points = scatter_base.mark_circle(size=110, color="#2563EB", opacity=0.75)
    # Equality reference line: from min to max observed
    max_axis = max(df["distinct_parties_on_docs"].max(), df["distinct_signer_emails"].max())
    ref_df = pd.DataFrame({"x": [0, max_axis], "y": [0, max_axis]})
    equality_line = (
        alt.Chart(ref_df)
        .mark_line(color="#9CA3AF", strokeDash=[6, 4])
        .encode(x="x:Q", y="y:Q")
    )

    scatter = alt.layer(equality_line, points).properties(height=320)
    st.altair_chart(scatter, use_container_width=True)

    st.markdown("#### Distribution of Parties per Transaction")
    # Distribution (how many transactions had 2 parties, 3 parties, etc.)
    dist = (
        alt.Chart(df)
        .mark_bar(color="#10B981", opacity=0.8)
        .encode(
            x=alt.X("distinct_parties_on_docs:Q", bin=False, title="Distinct Parties on Documents"),
            y=alt.Y("count():Q", title="Transactions"),
            tooltip=[
                alt.Tooltip("distinct_parties_on_docs:Q", title="Parties"),
                alt.Tooltip("count():Q", title="Transactions"),
            ],
        )
        .properties(height=220)
    )
    st.altair_chart(dist, use_container_width=True)

    # (Optional) quick KPI chips
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Transactions", len(df))
    with c2:
        st.metric("Mode: Parties per Tx", int(df["distinct_parties_on_docs"].mode().iloc[0]))
    with c3:
        pct_eq = (df["party_email_delta"] == 0).mean()
        st.metric("Pct with Parties == Emails", f"{pct_eq:.0%}")

def load_kpi06_df(text: str) -> pd.DataFrame:
    from io import StringIO
    df = pd.read_csv(StringIO(text), sep=r"\t", engine="python")

    # Parse date
    df["day"] = pd.to_datetime(df["day"])

    # Clean numeric columns (robust to pasted text)
    numeric_cols = [
        "envelope_sent",
        "recipient_delivered",
        "recipient_completed",
        "envelope_completed",
        "total_events",
    ]
    for col in numeric_cols:
        df[col] = pd.to_numeric(
            df[col].astype(str).str.extract(r"([+-]?\d+(?:\.\d+)?)")[0],
            errors="coerce"
        ).fillna(0).astype(float)

    # Sort and fill missing days across the observed range
    df = df.sort_values("day").set_index("day")
    full_index = pd.date_range(df.index.min(), df.index.max(), freq="D")
    df = df.reindex(full_index).fillna(0.0).rename_axis("day").reset_index()
    return df

def kpi06_section():
    st.subheader("KPI 06 – Envelope & Recipient Events (Daily)")

    df = load_kpi06_df(PASTED_DATA_KPI6)

    with st.expander("Show data", expanded=False):
        st.dataframe(df, use_container_width=True)

    # ------------------ Combo Chart ------------------
    base = alt.Chart(df).encode(
        x=alt.X("day:T", title="Day", axis=alt.Axis(labelAngle=0))
    )

    # Grouped bars for the 4 component metrics (left axis)
    bar_metrics = ["envelope_sent", "recipient_delivered", "recipient_completed", "envelope_completed"]
    bars = (
        base
        .transform_fold(bar_metrics, as_=["metric", "value"])
        .mark_bar(opacity=0.6)
        .encode(
            y=alt.Y("value:Q", title="Count"),
            color=alt.Color(
                "metric:N",
                scale=alt.Scale(
                    domain=bar_metrics,
                    range=["#6B7280", "#6366F1", "#10B981", "#F59E0B"]  # gray, indigo, green, amber
                ),
                title=""
            ),
            xOffset="metric:N",  # grouped (Altair 5+). If they stack, we can provide a fallback.
            tooltip=[
                alt.Tooltip("day:T", title="Day"),
                alt.Tooltip("metric:N", title="Metric"),
                alt.Tooltip("value:Q", title="Count"),
            ],
        )
    )

    # Line for total_events (right axis)
    total_line = (
        base
        .mark_line(point=True, color="#2563EB")
        .encode(
            y=alt.Y(
                "total_events:Q",
                title="Total Events",
                axis=alt.Axis(orient="right"),
            ),
            tooltip=[
                alt.Tooltip("day:T", title="Day"),
                alt.Tooltip("total_events:Q", title="Total Events"),
            ],
        )
    )

    combined = (
        alt.layer(bars, total_line)
        .resolve_scale(y="independent")   # bars on left axis, line on right axis
        .properties(height=320)
    )

    st.altair_chart(combined, use_container_width=True)

    # Quick summary chips
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Avg Total Events", f"{df['total_events'].mean():.1f}")
    with c2:
        st.metric("Max Total Events", int(df["total_events"].max()))
    with c3:
        st.metric("Days (Range)", f"{df['day'].min().date()} → {df['day'].max().date()}")
    with c4:
        st.metric("Observations", len(df))


def load_kpi07_df(text: str) -> pd.DataFrame:
    from io import StringIO
    df = pd.read_csv(StringIO(text), sep=r"\t", engine="python")

    # Parse date
    df["day"] = pd.to_datetime(df["day"])

    # Clean numeric columns
    for col in ["tcpa_yes", "tcpa_no", "total_records"]:
        df[col] = pd.to_numeric(
            df[col].astype(str).str.extract(r"([+-]?\d+(?:\.\d+)?)")[0],
            errors="coerce"
        ).fillna(0).astype(float)

    # Sort and fill missing calendar days in the observed range
    df = df.sort_values("day").set_index("day")
    full_index = pd.date_range(df.index.min(), df.index.max(), freq="D")
    df = df.reindex(full_index).fillna(0.0).rename_axis("day").reset_index()
    return df

def kpi07_section():
    st.subheader("KPI 07 – TCPA Consent (Daily)")

    df = load_kpi07_df(PASTED_DATA_KPI7)

    with st.expander("Show data", expanded=False):
        st.dataframe(df, use_container_width=True)

    # ------- Combo chart: grouped bars (yes/no) + line (total) -------
    base = alt.Chart(df).encode(
        x=alt.X("day:T", title="Day", axis=alt.Axis(labelAngle=0))
    )

    # Grouped bars for yes/no
    bars = (
        base
        .transform_fold(["tcpa_yes", "tcpa_no"], as_=["metric", "value"])
        .mark_bar(opacity=0.70)
        .encode(
            y=alt.Y("value:Q", title="Count"),
            color=alt.Color(
                "metric:N",
                scale=alt.Scale(domain=["tcpa_yes", "tcpa_no"],
                                range=["#10B981", "#EF4444"]),  # green yes, red no
                title=""
            ),
            xOffset="metric:N",  # grouped bars (Altair 5+)
            tooltip=[
                alt.Tooltip("day:T", title="Day"),
                alt.Tooltip("metric:N", title="Consent"),
                alt.Tooltip("value:Q", title="Count"),
            ],
        )
    )

    # Line for totals (right axis)
    total_line = (
        base
        .mark_line(point=True, color="#2563EB")
        .encode(
            y=alt.Y("total_records:Q", title="Total Records", axis=alt.Axis(orient="right")),
            tooltip=[
                alt.Tooltip("day:T", title="Day"),
                alt.Tooltip("total_records:Q", title="Total"),
            ],
        )
    )

    combined = (
        alt.layer(bars, total_line)
        .resolve_scale(y="independent")  # bars left axis, line right axis
        .properties(height=320)
    )

    st.altair_chart(combined, use_container_width=True)

    # Quick summary chips
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Total Records", int(df["total_records"].sum()))
    with c2:
        st.metric("TCPA Yes (Sum)", int(df["tcpa_yes"].sum()))
    with c3:
        st.metric("TCPA No (Sum)", int(df["tcpa_no"].sum()))
    with c4:
        share_yes = (df["tcpa_yes"].sum() / max(df["total_records"].sum(), 1))
        st.metric("Yes Share", f"{share_yes:.0%}")


def _parse_duration_to_seconds(text: str) -> float:
    """
    Parse duration strings like:
      - 'MM:SS'          e.g., '07:58'
      - 'MM:SS.s'        e.g., '07:58.8'
      - 'HH:MM:SS'       e.g., '1:07:58'
      - 'H:MM:SS.s'      e.g., '0:11:30.0'
    Returns seconds as float. Invalid inputs -> 0.0
    """
    s = str(text).strip()
    if not s or s.lower() in {"nan", "none"}:
        return 0.0
    try:
        parts = s.split(":")
        parts = [p.strip() for p in parts]
        if len(parts) == 2:
            mm, ss = parts
            minutes = float(mm)
            seconds = float(ss)
            return minutes * 60.0 + seconds
        elif len(parts) == 3:
            hh, mm, ss = parts
            hours = float(hh)
            minutes = float(mm)
            seconds = float(ss)
            return hours * 3600.0 + minutes * 60.0 + seconds
        else:
            # Fallback: try plain number (assume seconds)
            return float(s)
    except Exception:
        return 0.0

def load_kpi08_df(text: str) -> pd.DataFrame:
    from io import StringIO
    df = pd.read_csv(StringIO(text), sep=r"\t", engine="python")

    # Clean executed count
    df["executed_transactions"] = pd.to_numeric(
        df["executed_transactions"].astype(str).str.extract(r"([+-]?\d+(?:\.\d+)?)")[0],
        errors="coerce"
    ).fillna(0).astype(int)

    # Parse duration fields to seconds
    df["median_seconds"] = df["median_time_to_txn_execution"].apply(_parse_duration_to_seconds)
    df["p95_seconds"] = df["p95_time_to_txn_execution"].apply(_parse_duration_to_seconds)

    # Also keep minutes for display
    df["median_minutes"] = df["median_seconds"] / 60.0
    df["p95_minutes"] = df["p95_seconds"] / 60.0

    return df

def _fmt_mmss(seconds: float) -> str:
    """Format seconds to M:SS.s (e.g., 7:58.8)."""
    m = int(seconds // 60)
    s = seconds - m * 60
    return f"{m}:{s:04.1f}".replace(":0", ":")  # small cosmetic tweak

# def kpi08_section():
#     st.subheader("KPI 08 – Time to Transaction Execution (Diagnostics)")

#     # 1) Load and parse
#     df = load_kpi08_df(PASTED_DATA_KPI8)

#     # 2) Confirm routing and data
#     st.caption("Debug: Raw parsed DataFrame (head)")
#     st.dataframe(df.head(), use_container_width=True)

#     if df.empty:
#         st.error("KPI 08 dataframe is empty after parsing.")
#         return

#     # Pull the single summary row
#     row = df.iloc[0]

#     # 3) Metrics
#     c1, c2, c3 = st.columns(3)
#     with c1:
#         st.metric("Executed Transactions", int(row["executed_transactions"]))
#     with c2:
#         st.metric("Median Time to Execution", _fmt_mmss(row["median_seconds"]))
#     with c3:
#         st.metric("P95 Time to Execution", _fmt_mmss(row["p95_seconds"]))

#     # 4) Build a tiny chart dataframe
#     chart_df = pd.DataFrame({
#         "metric": ["Median", "P95"],
#         "minutes": [float(row["median_minutes"]), float(row["p95_minutes"])],
#         "seconds": [float(row["median_seconds"]), float(row["p95_seconds"])],
#     })

#     st.caption("Debug: Aggregated chart_df")
#     st.dataframe(chart_df, use_container_width=True)

#     # 5) First try: Streamlit's native bar chart (super reliable)
#     st.markdown("**Quick check: Native Streamlit bar chart (minutes)**")
#     # st.bar_chart expects a numeric index or a column set as index
#     st.bar_chart(chart_df.set_index("metric")["minutes"])

#     # 6) Second try: Simple Altair bar chart (no layering)
#     st.markdown("**Altair bar chart (minutes)**")
#     try:
#         max_minutes = max(chart_df["minutes"].max(), 1.0)
#         scale_max = max_minutes * 1.15

#         alt_bar = (
#             alt.Chart(chart_df.astype({"minutes": "float64"}))
#             .mark_bar(color="#2563EB", cornerRadius=4)
#             .encode(
#                 x=alt.X("minutes:Q", title="Minutes", scale=alt.Scale(domain=[0, scale_max])),
#                 y=alt.Y("metric:N", title="", sort=["P95", "Median"]),
#                 tooltip=[
#                     alt.Tooltip("metric:N", title="Metric"),
#                     alt.Tooltip("minutes:Q", title="Minutes", format=".1f"),
#                     alt.Tooltip("seconds:Q", title="Seconds", format=".1f"),
#                 ],
#             )
#             .properties(height=140)
#         )
#         st.altair_chart(alt_bar, use_container_width=True)
#     except Exception as e:
#         st.error(f"Altair chart error: {e}")

#     # 7) Final raw expander
#     with st.expander("Show raw KPI 08 data"):
#         view = df[[
#             "executed_transactions",
#             "median_time_to_txn_execution",
#             "p95_time_to_txn_execution",
#             "median_minutes",
#             "p95_minutes",
#         ]].rename(columns={
#             "median_minutes": "median_minutes (derived)",
#             "p95_minutes": "p95_minutes (derived)",
#         })
#         st.dataframe(view, use_container_width=True)


def kpi08_section():
    st.subheader("KPI 08 – Time to Transaction Execution")

    df = load_kpi08_df(PASTED_DATA_KPI8)
    if df.empty:
        st.warning("No KPI 08 data available.")
        return

    row = df.iloc[0]

    # -------------------- Metrics --------------------
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Executed Transactions", int(row["executed_transactions"]))
    with c2:
        st.metric("Median Time to Execution", _fmt_mmss(row["median_seconds"]))
    with c3:
        st.metric("P95 Time to Execution", _fmt_mmss(row["p95_seconds"]))

    # -------------------- Comparison chart (Median vs P95) --------------------
    chart_df = pd.DataFrame({
        "metric": ["Median", "P95"],
        "minutes": [float(row["median_minutes"]), float(row["p95_minutes"])],
        "label":  [_fmt_mmss(row["median_seconds"]), _fmt_mmss(row["p95_seconds"])],
    })

    # Guard against any dtype quirks
    chart_df["minutes"] = pd.to_numeric(chart_df["minutes"], errors="coerce").fillna(0.0)

    # Shared domain with headroom so labels don’t clip
    max_minutes = max(chart_df["minutes"].max(), 1.0)
    scale_max = max_minutes * 1.15

    bars = (
        alt.Chart(chart_df)
        .mark_bar(cornerRadius=4)
        .encode(
            x=alt.X("minutes:Q", title="Minutes", scale=alt.Scale(domain=[0, scale_max])),
            y=alt.Y("metric:N", title="", sort=["P95", "Median"]),  # P95 on top
            color=alt.Color("metric:N",
                            scale=alt.Scale(domain=["Median", "P95"], range=["#10B981", "#2563EB"]),
                            legend=None),
            tooltip=[alt.Tooltip("metric:N", title="Metric"),
                     alt.Tooltip("minutes:Q", title="Minutes", format=".1f"),
                     alt.Tooltip("label:N", title="Time (mm:ss.s)")],
        )
        .properties(height=140)
    )

    # On-bar labels (mm:ss.s)
    labels = (
        alt.Chart(chart_df)
        .mark_text(align="left", dx=6, color="#111827")
        .encode(
            x=alt.X("minutes:Q", scale=alt.Scale(domain=[0, scale_max])),
            y=alt.Y("metric:N", sort=["P95", "Median"]),
            text=alt.Text("label:N"),
        )
    )

    st.altair_chart(bars + labels, use_container_width=True)


def load_kpi09_df(text: str) -> pd.DataFrame:
    from io import StringIO
    df = pd.read_csv(StringIO(text), sep=r"\t", engine="python")

    # Parse timezone-aware timestamps
    df["first_seen_ts"] = pd.to_datetime(df["first_seen_ts"], utc=True, errors="coerce")
    df["last_seen_ts"]  = pd.to_datetime(df["last_seen_ts"],  utc=True, errors="coerce")

    # Clean users
    df["long_realty_users"] = pd.to_numeric(
        df["long_realty_users"].astype(str).str.extract(r"([+-]?\d+(?:\.\d+)?)")[0],
        errors="coerce"
    ).fillna(0).astype(int)

    # Derived span in seconds / hours / days
    df["span_seconds"] = (df["last_seen_ts"] - df["first_seen_ts"]).dt.total_seconds().clip(lower=0)
    df["span_hours"]   = df["span_seconds"] / 3600.0
    df["span_days"]    = df["span_hours"] / 24.0

    return df

def _fmt_span(days: float) -> str:
    """Format span-days into 'X days, HH:MM'."""
    import math
    total_minutes = int(round(days * 24 * 60))
    d = total_minutes // (24 * 60)
    rem = total_minutes % (24 * 60)
    hh = rem // 60
    mm = rem % 60
    if d > 0:
        return f"{d} day{'s' if d!=1 else ''}, {hh:02d}:{mm:02d}"
    else:
        return f"{hh:02d}:{mm:02d}"

def kpi09_section():
    st.subheader("KPI 09 – Long Realty Users Activity Window")

    df = load_kpi09_df(PASTED_DATA_KPI9)
    if df.empty or df["first_seen_ts"].isna().all() or df["last_seen_ts"].isna().all():
        st.warning("No KPI 09 data available.")
        return

    row = df.iloc[0]

    # -------------------- Metrics --------------------
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("First Seen (UTC)", row["first_seen_ts"].strftime("%Y-%m-%d %H:%M"))
    with c2:
        st.metric("Last Seen (UTC)", row["last_seen_ts"].strftime("%Y-%m-%d %H:%M"))
    with c3:
        st.metric("Long Realty Users", int(row["long_realty_users"]))
    with c4:
        st.metric("Active Span", _fmt_span(float(row["span_days"])))

    # -------------------- Timeline mini-chart --------------------
    # Build a tiny two-point dataframe for a horizontal bar using start/end
    tmin = pd.to_datetime(row["first_seen_ts"])
    tmax = pd.to_datetime(row["last_seen_ts"])

    timeline_df = pd.DataFrame({
        "label": ["Active Window"],
        "start": [tmin],
        "end":   [tmax],
    })

    # Altair: draw a horizontal bar from start to end
    # We’ll set the x-domain to the exact window for clarity
    base = alt.Chart(timeline_df)
    bar = (
        base
        .mark_bar(height=24, cornerRadius=6, color="#2563EB")
        .encode(
            x=alt.X("start:T", title=""),
            x2="end:T",
            y=alt.Y("label:N", title="")
        )
        .properties(height=70)
    )

    # Add tick markers for the endpoints
    ticks = (
        base
        .transform_fold(["start", "end"], as_=["kind", "time"])
        .mark_tick(thickness=2, size=24, color="#111827")
        .encode(
            x=alt.X("time:T"),
            y=alt.Y("label:N"),
            tooltip=[alt.Tooltip("kind:N", title="Edge"), alt.Tooltip("time:T", title="Timestamp (UTC)")]
        )
    )

    st.altair_chart(bar + ticks, use_container_width=True)

    # Optional: raw view
    with st.expander("Show raw KPI 09 data"):
        view = df[[
            "first_seen_ts", "last_seen_ts",
            "long_realty_users",
            "span_hours", "span_days"
        ]].rename(columns={
            "span_hours": "span_hours (derived)",
            "span_days":  "span_days (derived)"
        })
        st.dataframe(view, use_container_width=True)




def load_kpi10_df(text: str) -> pd.DataFrame:
    from io import StringIO
    df = pd.read_csv(StringIO(text), sep=r"\t", engine="python")

    # Parse date
    df["day"] = pd.to_datetime(df["day"])

    # Clean numeric
    df["users_touched"] = pd.to_numeric(
        df["users_touched"].astype(str).str.extract(r"([+-]?\d+(?:\.\d+)?)")[0],
        errors="coerce"
    ).fillna(0).astype(float)

    # Sort and fill missing calendar days across observed range with 0
    df = df.sort_values("day").set_index("day")
    full_index = pd.date_range(df.index.min(), df.index.max(), freq="D")
    df = df.reindex(full_index).fillna(0.0).rename_axis("day").reset_index()

    # Helpful derived metrics
    df["7d_rolling"] = df["users_touched"].rolling(window=7, min_periods=1).mean()

    return df

def kpi10_section():
    st.subheader("KPI 10 – Users Touched (Daily)")

    df = load_kpi10_df(PASTED_DATA_KPI10)

    # Quick metrics
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Total (Range)", int(df["users_touched"].sum()))
    with c2:
        st.metric("Average / Day", f"{df['users_touched'].mean():.1f}")
    with c3:
        st.metric("Max in a Day", int(df["users_touched"].max()))

    with st.expander("Show data", expanded=False):
        st.dataframe(df, use_container_width=True)

    # --------- Chart: Daily points + line, with optional 7-day rolling ---------
    base = alt.Chart(df).encode(x=alt.X("day:T", title="Day", axis=alt.Axis(labelAngle=0)))

    daily = (
        base.mark_line(point=True, color="#2563EB")
        .encode(
            y=alt.Y("users_touched:Q", title="Users Touched"),
            tooltip=[
                alt.Tooltip("day:T", title="Day"),
                alt.Tooltip("users_touched:Q", title="Users"),
            ],
        )
    )

    rolling = (
        base.mark_line(color="#10B981", strokeDash=[6, 4])
        .encode(
            y=alt.Y("7d_rolling:Q", title="Users Touched (7‑day Rolling)"),
            tooltip=[
                alt.Tooltip("day:T", title="Day"),
                alt.Tooltip("7d_rolling:Q", title="7‑day Avg", format=".1f"),
            ],
        )
    )

    chart = alt.layer(daily, rolling).properties(height=320)
    st.altair_chart(chart, use_container_width=True)


def load_kpi11_df(text: str) -> pd.DataFrame:
    from io import StringIO
    df = pd.read_csv(StringIO(text), sep=r"\t", engine="python")

    # Parse date
    df["event_date"] = pd.to_datetime(df["event_date"], errors="coerce")

    # Clean numeric columns
    for col in ["true_count", "false_count", "missing_count"]:
        df[col] = pd.to_numeric(
            df[col].astype(str).str.extract(r"([+-]?\d+(?:\.\d+)?)")[0],
            errors="coerce"
        ).fillna(0).astype(float)

    # Ensure expected metrics are strings
    df["metric"] = df["metric"].astype(str)

    return df

def kpi11_section():
    st.subheader("KPI 11 – Boolean Attribute Outcomes (Daily)")

    df = load_kpi11_df(PASTED_DATA_KPI11)
    if df.empty:
        st.warning("No KPI 11 data available.")
        return

    # Available boolean attributes (metrics)
    metrics = sorted(df["metric"].unique().tolist())

    # Tabs per metric for clean comparison
    tabs = st.tabs(metrics)

    for metric_name, tab in zip(metrics, tabs):
        with tab:
            mdf = df[df["metric"] == metric_name].copy()

            # Build continuous date range for the metric and fill missing days with zeros
            if not mdf["event_date"].isna().all():
                mdf = mdf.sort_values("event_date").set_index("event_date")
                full_idx = pd.date_range(mdf.index.min(), mdf.index.max(), freq="D")
                mdf = mdf.reindex(full_idx).fillna(0.0).rename_axis("event_date").reset_index()
            else:
                # Fallback if dates are all NaT (shouldn't happen with your data)
                mdf = mdf.copy()

            # Quick summary chips
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                st.metric("Days in Range", len(mdf))
            with c2:
                st.metric("True (Σ)", int(mdf["true_count"].sum()))
            with c3:
                st.metric("False (Σ)", int(mdf["false_count"].sum()))
            with c4:
                st.metric("Missing (Σ)", int(mdf["missing_count"].sum()))

            with st.expander("Show data", expanded=False):
                st.dataframe(mdf, use_container_width=True)

            # ---------- Stacked bars per day (true / false / missing) ----------
            plot_df = mdf.melt(
                id_vars=["event_date"],
                value_vars=["true_count", "false_count", "missing_count"],
                var_name="outcome",
                value_name="count"
            )

            # Friendly labels & colors
            color_domain = ["true_count", "false_count", "missing_count"]
            color_range = ["#10B981", "#EF4444", "#9CA3AF"]  # green, red, gray
            outcome_title_map = {
                "true_count": "True",
                "false_count": "False",
                "missing_count": "Missing"
            }

            base = alt.Chart(plot_df).encode(
                x=alt.X("event_date:T", title="Date", axis=alt.Axis(labelAngle=0))
            )

            stacked = (
                base
                .mark_bar()
                .encode(
                    y=alt.Y("count:Q", title=f"{metric_name} — Count"),
                    color=alt.Color(
                        "outcome:N",
                        scale=alt.Scale(domain=color_domain, range=color_range),
                        title="Outcome",
                    ),
                    tooltip=[
                        alt.Tooltip("event_date:T", title="Date"),
                        alt.Tooltip("outcome:N", title="Outcome"),
                        alt.Tooltip("count:Q", title="Count"),
                    ]
                )
                .transform_calculate(
                    outcome_label="datum.outcome == 'true_count' ? 'True' : datum.outcome == 'false_count' ? 'False' : 'Missing'"
                )
                .properties(height=320)
            )

            st.altair_chart(stacked, use_container_width=True)







# -------------------- Overview Section ---------------------
def overview_section():
    st.subheader("Overview")
    st.write(
        "Welcome to **CDP Insights** — a streamlined interface for data exploration, KPIs, and operational dashboards."
    )

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

# -------------------- App entrypoint -----------------------
# def main():
#     inject_css()
#     header()
#     page = sidebar()

#     if page == "Overview":
#         overview_section()
#     elif page == "KPI 01 – Transactions Created":
#         kpi01_section()
#     elif page == "KPI 02 – Documents Generated":   # adding the new page condition
#         kpi02_section() 
#     elif page == "KPI 03 – Documents Executed":   #
#         kpi03_section()
#     elif page == "KPI 04 – Daily Execution Rate":   # 
#         kpi04_section()
#     elif page == "KPI 05 – Parties per Transaction":   # 
#         kpi05_section()
#     elif page == "KPI 06 – Envelope & Recipient Events":   # 
#         kpi06_section()
#     elif page == "KPI 07 – TCPA Consent":   # 
#         kpi07_section()
#     elif page == "KPI 08 – Time to Execution":   # <-- add this block
#         kpi08_section()
# -------------------- App entrypoint -----------------------
def main():
    inject_css()
    header()
    page_label, page_handler = sidebar()

    # Optional debug line (remove later)
    # st.caption(f"DEBUG selected page: {page_label!r}")

    # Call the handler for the selected page
    page_handler()   



if __name__ == "__main__":
    main()