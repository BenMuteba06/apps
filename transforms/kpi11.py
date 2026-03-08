# transforms/kpi11.py
import pandas as pd

# This KPI tracks the counts of true, false, and missing values for a specific metric on a daily basis, which can indicate data quality issues and help identify trends in the underlying data over time.
def transform(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["event_date"] = pd.to_datetime(df["event_date"], errors="coerce")
    df["metric"] = df["metric"].astype(str).str.strip()  # ensure clean string, no floats
    for col in ["true_count", "false_count", "missing_count"]:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)
    # Drop rows where metric is empty/nan string — artifacts of bad parsing
    df = df[df["metric"].str.lower() != "nan"].reset_index(drop=True)
    return df # we don't need to reindex by day for this KPI since it's not strictly time-series based, but we could add a timestamp if needed for consistency with other KPIs