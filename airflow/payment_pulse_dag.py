# airflow/payment_pulse_dag.py
# India Payment Pulse — Airflow DAG
# Orchestrates full ETL pipeline daily at midnight

from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import sys
import os

sys.path.insert(0, '/opt/airflow/scripts')

default_args = {
    'owner':            'gopal_patil',
    'depends_on_past':  False,
    'start_date':       datetime(2026, 1, 1),
    'retries':          2,
    'retry_delay':      timedelta(minutes=5),
    'email_on_failure': False,
}

def task_generate():
    import os, glob
    from generate_data import generate_transactions, save_data
    os.chdir('/opt/airflow')
    df = generate_transactions(10000)
    save_data(df)
    print(f"Generated {len(df)} rows")

def task_extract():
    import glob
    from extract import extract
    files = sorted(glob.glob('/opt/airflow/data/raw/*.csv'))
    df = extract(files[-1])
    print(f"Extracted {len(df)} rows")

def task_transform():
    import glob
    from extract import extract
    from transform import transform
    files = sorted(glob.glob('/opt/airflow/data/raw/*.csv'))
    df = extract(files[-1])
    clean = transform(df)
    print(f"Cleaned {len(clean)} rows")

def task_anomaly():
    import glob
    from extract import extract
    from transform import transform
    from anomaly_detector import detect_anomalies, generate_anomaly_report
    files = sorted(glob.glob('/opt/airflow/data/raw/*.csv'))
    df = extract(files[-1])
    clean = transform(df)
    flagged = detect_anomalies(clean)
    report = generate_anomaly_report(flagged)
    print(f"Anomalies: {report}")

def task_load():
    import glob
    from extract import extract
    from transform import transform
    from anomaly_detector import detect_anomalies
    from load import load, save_parquet
    files = sorted(glob.glob('/opt/airflow/data/raw/*.csv'))
    df = extract(files[-1])
    clean = transform(df)
    flagged = detect_anomalies(clean)
    success = load(flagged)
    save_parquet(flagged)
    if not success:
        raise Exception("PostgreSQL load failed!")
    print(f"Loaded {len(flagged)} rows")

with DAG(
    dag_id            = 'india_payment_pulse',
    default_args      = default_args,
    description       = 'Daily UPI transaction ETL pipeline',
    schedule_interval = '@daily',
    catchup           = False,
    tags              = ['payments', 'etl', 'fintech'],
) as dag:

    t1 = PythonOperator(task_id='generate_data',      python_callable=task_generate)
    t2 = PythonOperator(task_id='extract',             python_callable=task_extract)
    t3 = PythonOperator(task_id='transform',           python_callable=task_transform)
    t4 = PythonOperator(task_id='detect_anomalies',    python_callable=task_anomaly)
    t5 = PythonOperator(task_id='load_to_postgresql',  python_callable=task_load)

    t1 >> t2 >> t3 >> t4 >> t5