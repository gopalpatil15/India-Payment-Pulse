# scripts/generate_data.py
# India Payment Pulse — Transaction Data Simulator
# Simulates 10,000 UPI transactions with intentional dirty data

import pandas as pd
import numpy as np
from faker import Faker
import random
from datetime import datetime, timedelta
import os

# Fix random seed so results are consistent every run
fake = Faker('en_IN')
random.seed(42)
np.random.seed(42)

# ── CONFIGURATION ─────────────────────────────────────────────────────────────
BANKS    = ["SBI", "HDFC", "ICICI", "Axis", "Kotak", "PNB", "BOB"]
STATUSES = ["SUCCESS", "FAILED", "PENDING", "REVERSED"]
UPI_APPS = ["PhonePe", "GPay", "Paytm", "BHIM", "AmazonPay"]
CATEGORIES = ["Food", "Transport", "Shopping", "Bills", "Transfer"]

def generate_transactions(n=10000):
    """
    Generate n simulated UPI transactions.
    Includes intentional dirty data:
    - 5% null amounts
    - 3% negative amounts
    - 2% duplicate txn_ids
    """
    print(f"Generating {n} transactions...")

    records = []
    base_date = datetime(2026, 1, 1)

    for i in range(n):

        # Normal transaction ID
        txn_id = f"UPI{str(i + 1).zfill(6)}"

        # Inject 2% duplicate txn_ids
        if random.random() < 0.02 and i > 100:
            txn_id = f"UPI{str(random.randint(1, i)).zfill(6)}"

        # Normal amount between ₹10 and ₹50,000
        amount = round(random.uniform(10, 50000), 2)

        # Inject 5% null amounts
        if random.random() < 0.05:
            amount = None

        # Inject 3% negative amounts
        elif random.random() < 0.03:
            amount = -abs(amount)

        # Random timestamp within January 2026
        timestamp = base_date + timedelta(
            minutes=random.randint(0, 43200)
        )

        records.append({
            "txn_id":         txn_id,
            "timestamp":      timestamp,
            "sender_bank":    random.choice(BANKS),
            "sender_account": f"ACC{random.randint(10000, 99999)}",
            "receiver_bank":  random.choice(BANKS),
            "upi_app":        random.choice(UPI_APPS),
            "amount":         amount,
            "status":         random.choice(STATUSES),
            "merchant":       fake.company(),
            "city":           fake.city(),
            "category":       random.choice(CATEGORIES)
        })

    df = pd.DataFrame(records)

    print(f"Generated:  {len(df)} rows")
    print(f"Null amounts:     {df['amount'].isnull().sum()}")
    print(f"Negative amounts: {(df['amount'] < 0).sum()}")
    print(f"Duplicate txn_ids:{df['txn_id'].duplicated().sum()}")

    return df


def save_data(df):
    """Save generated data to data/raw/ folder."""
    date_str = datetime.now().strftime("%Y%m%d")
    filepath = f"data/raw/transactions_{date_str}.csv"

    os.makedirs("data/raw", exist_ok=True)

    df.to_csv(filepath, index=False)
    print(f"\nSaved to: {filepath}")
    print(f"File size: {os.path.getsize(filepath) / 1024:.1f} KB")

    return filepath


# ── RUN ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 50)
    print("INDIA PAYMENT PULSE — Data Generator")
    print("=" * 50)

    df = generate_transactions(10000)
    filepath = save_data(df)

    print("\nSample data (first 5 rows):")
    print(df.head())
    print("\nData types:")
    print(df.dtypes)
    print("\nDay 1 Complete!")