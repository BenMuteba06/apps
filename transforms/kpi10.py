# transforms/kpi10.py
import pandas as pd

# This KPI tracks the number of unique users (by email) who interacted with the system each day.
def transform(df: pd.DataFrame) -> pd.DataFrame: 
    df = df.copy()
    df["day"] = pd.to_datetime(df["day"], errors="coerce")
    df["users_touched"] = pd.to_numeric(df["users_touched"], errors="coerce").fillna(0.0)
    df = df.sort_values("day").set_index("day")
    df = df.reindex(pd.date_range(df.index.min(), df.index.max(), freq="D")).fillna(0.0)
    df = df.rename_axis("day").reset_index()
    df["7d_rolling"] = df["users_touched"].rolling(window=7, min_periods=1).mean() # add a 7-day rolling average column for smoother trend analysis
    return df # we could also add a cumulative sum column if we want to track total unique users over time, but that might be less relevant for this KPI which is more about daily engagement.