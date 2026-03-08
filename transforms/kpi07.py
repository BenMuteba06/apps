# transforms/kpi07.py
import pandas as pd
# This KPI tracks the daily counts of TCPA consents (yes/no) and total records to provide insights into user preferences and compliance trends over time.
def transform(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["day"] = pd.to_datetime(df["day"], errors="coerce")
    for col in ["tcpa_yes", "tcpa_no", "total_records"]:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)
    df = df.sort_values("day").set_index("day")
    df = df.reindex(pd.date_range(df.index.min(), df.index.max(), freq="D")).fillna(0.0)
    return df.rename_axis("day").reset_index() # ensure 'day' is a column after reindexing, for consistency with other KPIs