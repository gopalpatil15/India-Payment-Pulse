# scripts/pipeline.py
# India Payment Pulse — Master Pipeline Orchestrator
# Runs: Generate → Extract → Transform → Anomaly Detection → Load

import os
import sys
import logging
from datetime import datetime


# Make sure script can import sibling modules regardless of where it's run from
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


def run_pipeline():
    """Run the full India Payment Pulse ETL pipeline end to end."""

    start_time = datetime.now()

    print("=" * 60)
    print("   INDIA PAYMENT PULSE — FULL PIPELINE RUN")
    print("=" * 60)
    print(f"   Started at: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60 + "\n")

    try:
        # ── STEP 1: GENERATE ────────────────────────────────────────────────
        print("STEP 1/5 — Generating transaction data...\n")
        from generate_data import generate_transactions, save_data
        raw_df = generate_transactions(10000)
        raw_filepath = save_data(raw_df)
        print()

        # ── STEP 2: EXTRACT ─────────────────────────────────────────────────
        print("STEP 2/5 — Extracting and validating...\n")
        from extract import extract
        extracted_df = extract(raw_filepath)
        print()

        # ── STEP 3: TRANSFORM ────────────────────────────────────────────────
        print("STEP 3/5 — Cleaning and transforming...\n")
        from transform import transform
        clean_df = transform(extracted_df)
        print()

        # ── STEP 4: ANOMALY DETECTION ────────────────────────────────────────
        print("STEP 4/5 — Detecting anomalies...\n")
        from anomaly_detector import detect_anomalies, generate_anomaly_report
        flagged_df = detect_anomalies(clean_df)
        anomaly_report = generate_anomaly_report(flagged_df)
        print()

        # ── STEP 5: LOAD ─────────────────────────────────────────────────────
        print("STEP 5/5 — Loading to PostgreSQL + Parquet...\n")
        from load import load, save_parquet
        load_success = load(flagged_df)
        parquet_path = save_parquet(flagged_df)
        print()

        # ── FINAL SUMMARY ────────────────────────────────────────────────────
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        print("=" * 60)
        print("   PIPELINE RUN COMPLETE")
        print("=" * 60)
        print(f"   Rows generated:       {len(raw_df):,}")
        print(f"   Rows after cleaning:  {len(clean_df):,}")
        print(f"   Anomalies flagged:    {sum(v for k, v in anomaly_report.items() if k != 'CLEAN'):,}")
        print(f"   Loaded to PostgreSQL: {'Yes' if load_success else 'FAILED'}")
        print(f"   Parquet backup:       {parquet_path}")
        print(f"   Total run time:       {duration:.2f} seconds")
        print(f"   Finished at:          {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)

        return True

    except Exception as e:
        logging.error(f"Pipeline failed: {e}")
        print("\nPIPELINE FAILED — see error above")
        return False


# ── RUN ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    success = run_pipeline()
    sys.exit(0 if success else 1)