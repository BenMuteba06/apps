# transforms/kpi10.py
import pandas as pd


def transform(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["day"] = pd.to_datetime(df["day"], errors="coerce")
    df["users_touched"] = pd.to_numeric(df["users_touched"], errors="coerce").fillna(0.0)
    df = df.sort_values("day").set_index("day")
    df = df.reindex(pd.date_range(df.index.min(), df.index.max(), freq="D")).fillna(0.0)
    df = df.rename_axis("day").reset_index()
    df["7d_rolling"] = df["users_touched"].rolling(window=7, min_periods=1).mean()
    return df