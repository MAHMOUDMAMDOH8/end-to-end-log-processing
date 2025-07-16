from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.operators.email import EmailOperator
from airflow.providers.slack.operators.slack_webhook import SlackWebhookOperator
from airflow.utils.dates import days_ago
from airflow.utils.task_group import TaskGroup
from datetime import timedelta
import psycopg2
import socket
import requests

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
    'start_date': days_ago(1),
}

def validate_postgres_data(**context):
    conn = psycopg2.connect(
        host="postgres",
        port=5432,
        database="airflow",
        user="airflow",
        password="airflow"
    )
    cursor = conn.cursor()
    validation_queries = [
        "SELECT COUNT(*) as null_count FROM order_complete_response WHERE order_id IS NULL",
        "SELECT COUNT(*) as row_count FROM order_complete_response"
    ]
    for query in validation_queries:
        cursor.execute(query)
        result = cursor.fetchone()
        if "null_count" in query:
            null_count = result[0]
            if null_count > 0:
                raise ValueError(f"Validation failed: {null_count} rows with null order_id found")
        else:
            row_count = result[0]
            if row_count == 0:
                raise ValueError("Validation failed: No rows found in order_complete_response")
    cursor.close()
    conn.close()

def notify_slack_success(context):
    slack_msg = f":tada: DAG {context['dag'].dag_id} completed successfully! Run ID: {context['run_id']} Execution Date: {context['execution_date']}"
    slack_notification = SlackWebhookOperator(
        task_id='slack_success_notification',
        slack_webhook_conn_id='slack_default',
        message=slack_msg
    )
    slack_notification.execute(context)

def notify_slack_failure(context):
    slack_msg = f":red_circle: DAG {context['dag'].dag_id} failed! Run ID: {context['run_id']} Execution Date: {context['execution_date']} Error: {context.get('exception', 'Unknown error')}"
    slack_notification = SlackWebhookOperator(
        task_id='slack_failure_notification',
        slack_webhook_conn_id='slack_default',
        message=slack_msg
    )
    slack_notification.execute(context)

def notify_slack_task_failure(context):
    slack_msg = f":warning: Task {context['task_instance'].task_id} failed in DAG {context['dag'].dag_id}! Run ID: {context['run_id']} Error: {context.get('exception', 'Unknown error')}"
    slack_notification = SlackWebhookOperator(
        task_id=f'slack_task_failure_notification_{context["task_instance"].task_id}',
        slack_webhook_conn_id='slack_default',
        message=slack_msg
    )
    slack_notification.execute(context)

def check_services_health(**context):
    services = [
        ('postgres', 'postgres', 5432),
        ('spark', 'spark', 8080)
    ]
    failed_services = []
    for service_name, host, port in services:
        if service_name == 'postgres':
            try:
                conn = psycopg2.connect(
                    host=host,
                    port=port,
                    database="airflow",
                    user="airflow",
                    password="airflow"
                )
                conn.close()
            except:
                failed_services.append(service_name)
        else:
            try:
                response = requests.get(f'http://{host}:{port}', timeout=5)
                if response.status_code != 200:
                    failed_services.append(service_name)
            except:
                failed_services.append(service_name)
    if failed_services:
        raise ValueError(f"Services down: {', '.join(failed_services)}")

with DAG(
    dag_id='spark_batch_job_dag',
    default_args=default_args,
    description='DAG for Spark batch job, dbt snapshots, and transformations',
    schedule_interval='*/10 * * * *',
    catchup=False,
    on_success_callback=notify_slack_success,
    on_failure_callback=notify_slack_failure
) as dag:
    with TaskGroup(group_id='check_services_group') as check_services_group:
        check_services = PythonOperator(
            task_id='check_services_health',
            python_callable=check_services_health,
            retries=2,
            retry_delay=timedelta(minutes=3),
            on_failure_callback=notify_slack_task_failure
        )
    with TaskGroup(group_id='validate_and_processing_group') as validate_and_processing_group:
        validate_data = PythonOperator(
            task_id='validate_postgres_data',
            python_callable=validate_postgres_data,
            retries=2,
            retry_delay=timedelta(minutes=3),
            on_failure_callback=notify_slack_task_failure
        )
        spark_batch_task = BashOperator(
            task_id='spark_batch_task',
            bash_command="docker exec spark /bin/bash -c \"cd /opt/spark/scripts/spark_jop && spark-submit --master spark://spark:7077 batch_jop.py\"",
            retries=3,
            retry_delay=timedelta(minutes=5),
            on_failure_callback=notify_slack_task_failure
        )
        validate_data >> spark_batch_task
    with TaskGroup(group_id='dbt_group') as dbt_group:
        dbt_snapshot_task = BashOperator(
            task_id='dbt_snapshot_task',
            bash_command="docker exec airflow-scheduler /bin/bash -c \"cd /opt/airflow/dbt && dbt snapshot\"",
            retries=2,
            retry_delay=timedelta(minutes=3),
            on_failure_callback=notify_slack_task_failure
        )
        dbt_run_task = BashOperator(
            task_id='dbt_run_task',
            bash_command="docker exec airflow-scheduler /bin/bash -c \"cd /opt/airflow/dbt && dbt run\"",
            retries=2,
            retry_delay=timedelta(minutes=3),
            on_failure_callback=notify_slack_task_failure
        )
        dbt_snapshot_task >> dbt_run_task
    send_email = EmailOperator(
        task_id='send_email_service_failure',
        to='admin@example.com',
        subject='Service Failure Alert',
        html_content="Services {{ ti.xcom_pull(task_ids='check_services_health') }} are down. Please check the system.",
        trigger_rule='all_failed'
    )
    check_services_group >> validate_and_processing_group >> dbt_group
    check_services_group >> send_email

