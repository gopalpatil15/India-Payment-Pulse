# scripts/load.py
# India Payment Pulse — Load Layer
# Loads clean DataFrame into PostgreSQL + saves Parquet backup

import os
from datetime import datetime

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
import logging

# ── LOGGING ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# ── CONFIG ────────────────────────────────────────────────────────────────────
load_dotenv()
DB_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:7280@localhost:5432/payment_pulse"
)


# ── LOAD TO POSTGRESQL ────────────────────────────────────────────────────────
def load(df, table_name="transactions"):
    """
    Load clean DataFrame into PostgreSQL.
    Returns True if success, False if failed.
    """
    try:
        # Step 1 — create engine
        engine = create_engine(DB_URL)

        # Step 2 — log what we are about to load
        logging.info(f"Loading {len(df):,} rows into table: {table_name}")

        # Step 3 — push DataFrame into PostgreSQL
        df.to_sql(
            table_name,
            engine,
            if_exists="append",   # add rows — do not delete existing data
            index=False            # do not save DataFrame index as a column
        )

        # Step 4 — verify load worked
        with engine.connect() as conn:
            result = conn.execute(
                text(f"SELECT COUNT(*) FROM {table_name}")
            )
            total_rows = result.fetchone()[0]

        # Step 5 — log success
        logging.info("Load successful!")
        logging.info(f"Total rows in {table_name}: {total_rows:,}")

        return True

    except Exception as e:
        logging.error(f"Load failed: {e}")
        return False


# ── SAVE PARQUET BACKUP ───────────────────────────────────────────────────────
def save_parquet(df, folder="data/clean"):
    """
    Save clean DataFrame as Parquet file.
    Parquet = smaller file, faster reads than CSV.
    """
    try:
        os.makedirs(folder, exist_ok=True)

        date_str = datetime.now().strftime("%Y%m%d")
        filepath = os.path.join(folder, f"transactions_{date_str}.parquet")

        df.to_parquet(filepath, index=False)

        size_kb = os.path.getsize(filepath) / 1024
        logging.info(f"Parquet saved: {filepath} ({size_kb:.1f} KB)")

        return filepath

    except Exception as e:
        logging.error(f"Parquet save failed: {e}")
        return None


# ── PIPELINE SUMMARY ──────────────────────────────────────────────────────────
def print_summary(raw_count, clean_count, table_name, parquet_path):
    """Print a clean pipeline summary report."""
    dropped = raw_count - clean_count
    drop_rate = (dropped / raw_count * 100) if raw_count > 0 else 0

    print("\n" + "=" * 50)
    print("   INDIA PAYMENT PULSE — PIPELINE SUMMARY")
    print("=" * 50)
    print(f"   Rows extracted:   {raw_count:,}")
    print(f"   Rows cleaned:     {clean_count:,}")
    print(f"   Rows dropped:     {dropped:,}  ({drop_rate:.1f}%)")
    print(f"   Loaded into:      {table_name}")
    print(f"   Parquet saved:    {parquet_path}")
    print(f"   Run time:         {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50 + "\n")


# ── RUN ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import sys
    sys.path.append("scripts")

    from extract import extract
    from transform import transform

    raw_folder = "data/raw"
    files = sorted(os.listdir(raw_folder))

    if not files:
        logging.error("No raw files found in data/raw/")
        sys.exit(1)

    latest = os.path.join(raw_folder, files[-1])

    print("Starting India Payment Pulse pipeline...")

    raw_df = extract(latest)
    clean_df = transform(raw_df)

    success = load(clean_df)
    parquet_path = save_parquet(clean_df)

    if success:
        print_summary(
            raw_count=len(raw_df),
            clean_count=len(clean_df),
            table_name="transactions",
            parquet_path=parquet_path
        )
    else:
        print("\nPipeline failed — check logs above")
        sys.exit(1)