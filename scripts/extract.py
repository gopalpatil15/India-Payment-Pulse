# scripts/extract.py
# India Payment Pulse — Extract Layer
# Reads raw transaction CSV and validates schema

import pandas as pd
import logging
import os
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

EXPECTED_COLUMNS = [
    "txn_id", "timestamp", "sender_bank",
    "receiver_bank", "upi_app", "amount",
    "status", "merchant", "city", "category"
]

def extract(filepath):
    """Read raw CSV and validate schema."""
    try:
        logging.info(f"Extracting from: {filepath}")

        # Read CSV
        df = pd.read_csv(filepath)

        # Check file is not empty
        if df.empty:
            raise ValueError("CSV file is empty!")

        # Check all expected columns exist
        missing = set(EXPECTED_COLUMNS) - set(df.columns)
        if missing:
            raise ValueError(f"Missing columns: {missing}")

        logging.info(f"Rows loaded:    {len(df):,}")
        logging.info(f"Columns found:  {list(df.columns)}")
        logging.info(f"Null counts:\n{df.isnull().sum()}")

        return df

    except FileNotFoundError:
        logging.error(f"File not found: {filepath}")
        raise
    except Exception as e:
        logging.error(f"Extraction failed: {e}")
        raise


if __name__ == "__main__":
    # Find latest file in data/raw/
    raw_folder = "data/raw"
    files = sorted(os.listdir(raw_folder))
    latest = os.path.join(raw_folder, files[-1])

    df = extract(latest)

    print("\nSample data:")
    print(df.head(3))
    print(f"\nShape: {df.shape}")
    print("\nExtract complete!")