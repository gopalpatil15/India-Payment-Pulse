# scripts/transform.py
# India Payment Pulse — Transform Layer
# Cleans raw transactions — removes nulls, duplicates, negatives

import pandas as pd
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def transform(df):
    """Clean and transform raw transaction DataFrame."""

    rows_before = len(df)
    logging.info(f"Transform started. Rows: {rows_before:,}")

    # 1. Convert amount to numeric — invalid values become NaN
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce")

    # 2. Drop rows with null txn_id
    df = df.dropna(subset=["txn_id"])

    # 3. Drop rows with null or negative amount
    df = df.dropna(subset=["amount"])
    df = df[df["amount"] > 0]

    # 4. Remove duplicate txn_ids — keep first
    df = df.drop_duplicates(subset=["txn_id"], keep="first")

    # 5. Standardize status to uppercase
    df["status"] = df["status"].str.strip().str.upper()

    # 6. Standardize city to title case
    df["city"] = df["city"].str.strip().str.title()

    # 7. Parse timestamp
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    df = df.dropna(subset=["timestamp"])

    # 8. Add processing fee column — UPI fee = 0.2% of amount
    df["processing_fee"] = (df["amount"] * 0.002).round(4)

    # 9. Add hour of day — useful for KPI analysis
    df["hour"] = df["timestamp"].dt.hour

    # 10. Reset index
    df = df.reset_index(drop=True)

    rows_after = len(df)
    rows_dropped = rows_before - rows_after

    logging.info(f"Rows after clean: {rows_after:,}")
    logging.info(f"Rows dropped:     {rows_dropped:,}")
    logging.info(f"Drop rate:        {rows_dropped/rows_before*100:.1f}%")

    return df


if __name__ == "__main__":
    from extract import extract
    import os

    raw_folder = "data/raw"
    files = sorted(os.listdir(raw_folder))
    latest = os.path.join(raw_folder, files[-1])

    raw_df = extract(latest)
    clean_df = transform(raw_df)

    print("\nCleaned sample:")
    print(clean_df.head(3))
    print(f"\nColumns now: {list(clean_df.columns)}")
    print("\nTransform complete!")