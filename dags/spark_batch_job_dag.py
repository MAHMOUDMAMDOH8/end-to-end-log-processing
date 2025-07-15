from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=2),
}

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


