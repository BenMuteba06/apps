# transforms/kpi05.py
import pandas as pd
# This KPI calculates the difference between the number of distinct parties on documents and the number of distinct signer emails, which can indicate the level of collaboration and potential bottlenecks in the signing process.
def transform(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    for col in ["distinct_parties_on_docs", "distinct_signer_emails"]:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)
    df["party_email_delta"] = df["distinct_parties_on_docs"] - df["distinct_signer_emails"]
    return df # we don't need to reindex by day for this KPI since it's not time-series based, but we could add a timestamp if needed for consistency with other KPIs