# transforms/kpi03.py
import pandas as pd
# This KPI tracks the number of documents executed each day, which can indicate successful completions and user engagement.
def transform(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["day"] = pd.to_datetime(df["day"], errors="coerce")
    df["documents_executed"] = pd.to_numeric(df["documents_executed"], errors="coerce").fillna(0.0)
    df = df.sort_values("day").set_index("day")
    df = df.reindex(pd.date_range(df.index.min(), df.index.max(), freq="D")).fillna(0.0)
    return df.rename_axis("day").reset_index() # ensure 'day' is a column after reindexing, for consistency with other KPIs