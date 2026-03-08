# transforms/kpi09.py
import pandas as pd

# This KPI tracks the time span between the first and last interaction of users with the system, which can indicate user engagement duration and potential issues in user experience if the span is unusually long or short.
def transform(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["first_seen_ts"] = pd.to_datetime(df["first_seen_ts"], utc=True, errors="coerce")
    df["last_seen_ts"]  = pd.to_datetime(df["last_seen_ts"],  utc=True, errors="coerce")
    df["long_realty_users"] = pd.to_numeric(df["long_realty_users"], errors="coerce").fillna(0).astype(int)
    df["span_seconds"] = (df["last_seen_ts"] - df["first_seen_ts"]).dt.total_seconds().clip(lower=0)
    df["span_hours"]   = df["span_seconds"] / 3600.0
    df["span_days"]    = df["span_hours"] / 24.0
    return df # we don't need to reindex by day for this KPI since it's not time-series based, but we could add a timestamp if needed for consistency with other KPIs