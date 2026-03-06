# transforms/kpi06.py
import pandas as pd

NUMERIC_COLS = [
    "envelope_sent", "recipient_delivered",
    "recipient_completed", "envelope_completed", "total_events",
]

def transform(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["day"] = pd.to_datetime(df["day"], errors="coerce")
    for col in NUMERIC_COLS:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)
    df = df.sort_values("day").set_index("day")
    df = df.reindex(pd.date_range(df.index.min(), df.index.max(), freq="D")).fillna(0.0)
    return df.rename_axis("day").reset_index()