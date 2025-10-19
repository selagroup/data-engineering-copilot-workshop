"""
Starter DAG for workshop participants to complete.
GitHub Copilot will help build this into a full ETL pipeline.
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator