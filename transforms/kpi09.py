# transforms/kpi09.py
import pandas as pd


def transform(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["first_seen_ts"] = pd.to_datetime(df["first_seen_ts"], utc=True, errors="coerce")
    df["last_seen_ts"]  = pd.to_datetime(df["last_seen_ts"],  utc=True, errors="coerce")
    df["long_realty_users"] = pd.to_numeric(df["long_realty_users"], errors="coerce").fillna(0).astype(int)
    df["span_seconds"] = (df["last_seen_ts"] - df["first_seen_ts"]).dt.total_seconds().clip(lower=0)
    df["span_hours"]   = df["span_seconds"] / 3600.0
    df["span_days"]    = df["span_hours"] / 24.0
    return df