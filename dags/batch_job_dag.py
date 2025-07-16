from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta
import os

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=2),
}

profiles_path = '/opt/airflow/dbt/profiles.yml'
project_path = '/opt/airflow/dbt/Ecommerce_model/dbt_project.yml'

dag = DAG(
    'spark_batch_job',
    default_args=default_args,
    description='Run Spark batch job every 10 minutes',
    schedule='*/10 * * * *',
    start_date=datetime(2024, 1, 1),
    catchup=False,
)

spark_batch_task = BashOperator(
    task_id='run_spark_batch_job',
    bash_command='spark-submit --jars /tmp/postgresql-42.7.3.jar /opt/airflow/scripts/spark_jop/batch_jop.py',
    dag=dag,
)
# dbt snapshot
dbt_snapshot_task = BashOperator(
    task_id='run_dbt_snapshot',
    bash_command=f'dbt snapshot --profiles-dir {os.path.dirname(profiles_path)} --project-dir {os.path.dirname(project_path)}',
    dag=dag,
)

# dbt run
dbt_run_task = BashOperator(
    task_id='run_dbt_run',
    bash_command=f'dbt run --profiles-dir {os.path.dirname(profiles_path)} --project-dir {os.path.dirname(project_path)}',
    dag=dag,
)

spark_batch_task >> dbt_snapshot_task >> dbt_run_task




