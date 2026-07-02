
# India Payment Pulse 🇮🇳

An end-to-end ETL data pipeline simulating India's UPI payment ecosystem —
built to automate the transaction verification, anomaly detection, and
reconciliation workflows I managed manually for **Rs.8 crore+** in real
financial operations.

---

## Why I Built This

In a prior role I manually reconciled high-value financial transactions —
catching discrepancies, validating amounts, and maintaining audit records
for Rs.8 crore+ in payments. This project automates that exact workflow
using Python and SQL, replacing manual verification with a production-style
automated pipeline.

---

## Pipeline Architecture

```
Raw CSV (10,000 UPI transactions)
        ↓
   STEP 1: GENERATE — simulate realistic dirty UPI data
        ↓
   STEP 2: EXTRACT — schema validation + null audit
        ↓
   STEP 3: TRANSFORM — clean, dedupe, feature engineering
        ↓
   STEP 4: ANOMALY DETECTION — NumPy percentile + velocity fraud checks
        ↓
   STEP 5: LOAD — PostgreSQL (SQLAlchemy) + Parquet backup
        ↓
   ORCHESTRATION — Apache Airflow DAG (daily schedule)
```

---

## Confirmed Pipeline Output

```
============================================================
   INDIA PAYMENT PULSE — FULL PIPELINE RUN
============================================================
   Rows generated:       10,000
   Rows after cleaning:  9,046
   Anomalies flagged:    475
   Loaded to PostgreSQL: Yes
   Parquet backup:       data/clean/transactions_20260702.parquet
   Total run time:       16.98 seconds
   Finished at:          2026-07-02 10:07:05
============================================================
```

---

## Anomaly Detection Report

```
==================================================
   ANOMALY DETECTION REPORT
==================================================
   Total transactions analysed: 9,046
   CLEAN                   8,571  ( 94.7%)
   VELOCITY_ANOMALY          384  (  4.2%)
   HIGH_VALUE                 91  (  1.0%)
==================================================
   TOP 5 ANOMALIES BY AMOUNT:
   txn_id      amount  sender_bank  anomaly_flag
   UPI003183  49999.44         PNB    HIGH_VALUE
   UPI007710  49998.93         PNB    HIGH_VALUE
   UPI006180  49986.75       Kotak    HIGH_VALUE
   UPI005372  49983.90         SBI    HIGH_VALUE
   UPI004704  49977.13       ICICI    HIGH_VALUE
==================================================
```

**Detection logic:**
- `HIGH_VALUE` — transactions above the 99th percentile (Rs.49,475+)
- `VELOCITY_ANOMALY` — same sender account, multiple transactions within 2 minutes

---

## Pipeline Results Summary

| Stage | Metric |
|---|---|
| Rows generated | 10,000 |
| Null amounts injected | ~500 (5%) |
| Negative amounts injected | ~288 (3%) |
| Duplicate txn_ids injected | ~192 (2%) |
| Rows after cleaning | 9,046 (9.5% dropped) |
| HIGH_VALUE anomalies | 91 (1.0%) |
| VELOCITY_ANOMALY | 384 (4.2%) |
| Clean transactions | 8,571 (94.7%) |
| Loaded to PostgreSQL | 9,046 rows |
| Parquet backup | 467.8 KB |
| Total run time | 16.98 seconds |

---

## Tech Stack

| Layer | Tools |
|---|---|
| Data Generation | Python, Faker (en\_IN locale), NumPy |
| Extract | pandas, schema validation, logging |
| Transform | pandas, feature engineering |
| Anomaly Detection | NumPy percentile analysis |
| Load | PostgreSQL, SQLAlchemy, Parquet (pyarrow) |
| Orchestration | Apache Airflow DAG |

---

## Project Structure

```
India-Payment-Pulse/
├── scripts/
│   ├── generate_data.py      # Simulates 10K UPI transactions with dirty data
│   ├── extract.py            # Schema validation + null audit
│   ├── transform.py          # Cleaning, dedup, feature engineering
│   ├── anomaly_detector.py   # Percentile + velocity fraud detection
│   ├── load.py               # PostgreSQL load + Parquet backup
│   └── main.py               # Single command orchestrator
├── airflow/
│   └── payment_pulse_dag.py  # Airflow DAG — daily schedule, 5 task dependencies
├── data/
│   ├── raw/                  # Generated CSVs (gitignored)
│   └── clean/                # Parquet outputs (gitignored)
├── requirements.txt
├── .gitignore
└── README.md
```

---

## How to Run

```bash
# Install dependencies
pip install -r requirements.txt

# Configure database (copy and edit)
copy .env.example .env

# Run the full pipeline in one command
python scripts/main.py
```

---

## Airflow Orchestration

The pipeline is designed for daily automated execution via Apache Airflow.
The DAG (`airflow/payment_pulse_dag.py`) defines 5 sequential tasks with:
- Retry logic: 2 retries with 5-minute delay
- Daily schedule: `@daily`
- Tags: `payments`, `etl`, `fintech`

```
generate_data >> extract >> transform >> detect_anomalies >> load_to_postgresql
```

---

## Data Quality Checks Built Into Pipeline

- Null value detection and removal
- Duplicate `txn_id` deduplication (keep first occurrence)
- Negative amount filtering
- Invalid timestamp removal
- Schema validation — rejects files with missing columns before processing

---

## What I'd Add Next

- [ ] Streamlit dashboard for live KPI monitoring
- [ ] FastAPI REST endpoints (`/transactions`, `/anomalies`, `/kpis`)
- [ ] Reconciliation module comparing pipeline vs bank statement
- [ ] Cloud deployment (AWS S3 + RDS)
- [ ] Unit tests with pytest

---

## Author

**Gopal Patil**
[GitHub](https://github.com/gopalpatil15) ·
bhamaregopal2003@gmail.com
```
