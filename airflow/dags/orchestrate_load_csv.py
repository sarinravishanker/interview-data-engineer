from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import logging
import sys
sys.path.append('/opt/airflow/scripts')  # Ensure the scripts directory is in the Python path

# Log a message to confirm the DAG is being loaded
logging.info("Loading DAG: orchestrate_load_csv")

# Import the executable function from load_csv.py
from load_csv import execute_load_csv

# Define default arguments for the DAG
default_args = {
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 0,
    "retry_delay": timedelta(minutes=5),
}

# Define the DAG
with DAG(
    dag_id="orchestrate_load_csv",
    default_args=default_args,
    description="Orchestrate and schedule the execution of load_csv.py",
    schedule_interval="0 8 * * *",  # Every day at 8 AM
    start_date=datetime(2025, 4, 24),
    catchup=False,
) as dag:

    # Task to execute the load_csv.py logic
    execute_load_csv_task = PythonOperator(
        task_id="execute_load_csv",
        python_callable=execute_load_csv,
    )

    execute_load_csv_task
