from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
from scripts.load_csv import main

# Define default arguments for the DAG
default_args = {
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

# Define the Python function to execute the main function from load_csv.py
def run_load_csv_script():
    main()

# Define the DAG
with DAG(
    dag_id="load_csv_to_pg",
    default_args=default_args,
    description="Load CSV data into PostgreSQL",
    schedule_interval="0 7 * * *",  # Every day at 7 AM
    start_date=datetime(2025, 4, 24),
    catchup=False,
) as dag:

    # Task to execute the load_csv.py script
    load_csv_task = PythonOperator(
        task_id="load_csv_to_postgres",
        python_callable=run_load_csv_script,
    )

    load_csv_task
