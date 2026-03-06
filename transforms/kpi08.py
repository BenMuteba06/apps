# transforms/kpi08.py
import pandas as pd


def _parse_duration_to_seconds(text: str) -> float:
    """Parse 'MM:SS', 'MM:SS.s', 'HH:MM:SS' strings to seconds."""
    s = str(text).strip()
    if not s or s.lower() in {"nan", "none"}:
        return 0.0
    try:
        parts = s.split(":")
        if len(parts) == 2:
            return float(parts[0]) * 60 + float(parts[1])
        elif len(parts) == 3:
            return float(parts[0]) * 3600 + float(parts[1]) * 60 + float(parts[2])
        return float(s)
    except Exception:
        return 0.0


def transform(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["executed_transactions"] = pd.to_numeric(df["executed_transactions"], errors="coerce").fillna(0).astype(int)
    df["median_seconds"] = df["median_time_to_txn_execution"].apply(_parse_duration_to_seconds)
    df["p95_seconds"]    = df["p95_time_to_txn_execution"].apply(_parse_duration_to_seconds)
    df["median_minutes"] = df["median_seconds"] / 60.0
    df["p95_minutes"]    = df["p95_seconds"] / 60.0
    return df