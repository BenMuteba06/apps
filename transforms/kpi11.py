# transforms/kpi11.py
import pandas as pd


def transform(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["event_date"] = pd.to_datetime(df["event_date"], errors="coerce")
    df["metric"] = df["metric"].astype(str).str.strip()  # ensure clean string, no floats
    for col in ["true_count", "false_count", "missing_count"]:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)
    # Drop rows where metric is empty/nan string — artifacts of bad parsing
    df = df[df["metric"].str.lower() != "nan"].reset_index(drop=True)
    return df