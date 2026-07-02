# scripts/anomaly_detector.py
# India Payment Pulse — Anomaly Detection Layer
# Uses NumPy percentile analysis to flag suspicious transactions

import pandas as pd
import numpy as np
import logging
import os

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


# ── ANOMALY DETECTION ─────────────────────────────────────────────────────────
def detect_anomalies(df):
    """
    Flag suspicious transactions using statistical analysis.
    Adds an 'anomaly_flag' column to the DataFrame.
    """
    df = df.copy()  # avoid SettingWithCopyWarning
    df["anomaly_flag"] = "CLEAN"

    # ── Check 1: High-value outliers (above 99th percentile) ──────────────────
    threshold_99 = np.percentile(df["amount"].dropna(), 99)
    high_value_mask = df["amount"] > threshold_99
    df.loc[high_value_mask, "anomaly_flag"] = "HIGH_VALUE"

    logging.info(f"99th percentile threshold: Rs.{threshold_99:,.2f}")
    logging.info(f"High value transactions flagged: {high_value_mask.sum():,}")

    # ── Check 2: Round number amounts (common fraud pattern) ──────────────────
    # Real transactions rarely land exactly on round thousands
    round_mask = (df["amount"] % 1000 == 0) & (df["anomaly_flag"] == "CLEAN")
    df.loc[round_mask, "anomaly_flag"] = "ROUND_AMOUNT"

    logging.info(f"Round amount transactions flagged: {round_mask.sum():,}")

    # ── Check 3: Velocity anomaly (same sender, many transactions, short time) ─
    df_sorted = df.sort_values(["sender_bank", "timestamp"])
    df_sorted["time_diff_mins"] = (
        df_sorted.groupby("sender_bank")["timestamp"]
        .diff()
        .dt.total_seconds() / 60
    )

    # Flag if less than 2 minutes between transactions from same bank
    velocity_mask = (
        (df_sorted["time_diff_mins"] < 2) &
        (df_sorted["time_diff_mins"].notna()) &
        (df_sorted["anomaly_flag"] == "CLEAN")
    )
    df_sorted.loc[velocity_mask, "anomaly_flag"] = "VELOCITY_ANOMALY"

    logging.info(f"Velocity anomalies flagged: {velocity_mask.sum():,}")

    # Drop helper column, restore original order
    df_sorted = df_sorted.drop(columns=["time_diff_mins"])
    df_final = df_sorted.sort_index()

    return df_final


# ── ANOMALY REPORT ─────────────────────────────────────────────────────────────
def generate_anomaly_report(df):
    """Print a summary report of all detected anomalies."""
    total_rows = len(df)
    anomaly_counts = df["anomaly_flag"].value_counts()

    print("\n" + "=" * 50)
    print("   ANOMALY DETECTION REPORT")
    print("=" * 50)
    print(f"   Total transactions analysed: {total_rows:,}")
    print()

    for flag, count in anomaly_counts.items():
        pct = (count / total_rows) * 100
        print(f"   {flag:20s} {count:>8,}  ({pct:>5.1f}%)")

    print("=" * 50)

    # Show top 5 highest value anomalies for investigation
    anomalies = df[df["anomaly_flag"] != "CLEAN"]
    if not anomalies.empty:
        print("\n   TOP 5 ANOMALIES BY AMOUNT:")
        top5 = anomalies.nlargest(5, "amount")[
            ["txn_id", "amount", "sender_bank", "anomaly_flag"]
        ]
        print(top5.to_string(index=False))

    print()
    return anomaly_counts.to_dict()


# ── RUN ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import sys
    sys.path.append("scripts")

    from extract import extract
    from transform import transform

    raw_folder = "scripts/data/raw"
    files = sorted(os.listdir(raw_folder))

    if not files:
        logging.error("No raw files found in scripts/data/raw/")
        sys.exit(1)

    latest = os.path.join(raw_folder, files[-1])

    print("Running anomaly detection pipeline...")

    raw_df = extract(latest)
    clean_df = transform(raw_df)
    flagged_df = detect_anomalies(clean_df)

    report = generate_anomaly_report(flagged_df)

    print("Anomaly detection complete!")