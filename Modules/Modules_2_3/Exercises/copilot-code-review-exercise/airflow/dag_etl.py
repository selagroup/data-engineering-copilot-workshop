from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import subprocess

default_args = {
    "owner": "data-team",
    "start_date": datetime.utcnow(),
    "retries": 0,
}

with DAG(
    "toy_etl",
    default_args=default_args,
    schedule_interval="@daily",
    catchup=True,
) as dag:

    def run_etl():
        subprocess.check_call(["python", "etl/etl.py"])

    etl_task = PythonOperator(task_id="run_etl", python_callable=run_etl)
