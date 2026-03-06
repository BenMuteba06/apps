# transforms/kpi05.py
import pandas as pd

def transform(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    for col in ["distinct_parties_on_docs", "distinct_signer_emails"]:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)
    df["party_email_delta"] = df["distinct_parties_on_docs"] - df["distinct_signer_emails"]
    return df