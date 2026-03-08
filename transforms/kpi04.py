# transforms/kpi04.py
import pandas as pd
# This KPI calculates the execution rate (documents executed / documents generated) each day, which can indicate the efficiency of the document processing and user follow-through.
def transform(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["day"] = pd.to_datetime(df["day"], errors="coerce")

    for col in ["generated", "executed", "execution_rate"]:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)

    # Recompute rate where it's zero but generated > 0
    mask = (df["generated"] > 0) & (df["execution_rate"] == 0)
    df.loc[mask, "execution_rate"] = df.loc[mask, "executed"] / df.loc[mask, "generated"]
    df["execution_rate"] = df["execution_rate"].clip(0, 1)

    df = df.sort_values("day").set_index("day")
    df = df.reindex(pd.date_range(df.index.min(), df.index.max(), freq="D")).fillna(0.0)
    return df.rename_axis("day").reset_index() # ensure 'day' is a column after reindexing, for consistency with other KPIs