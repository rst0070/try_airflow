from datetime import datetime, timedelta
from airflow import DAG
from airflow.providers.postgres.operators.postgres import PostgresOperator

default_args = {
    'owner': 'rst0070',
    'retries': 5,
    'retry_delay': timedelta(minutes=5)
}

with DAG(
    dag_id='dag_f_postgresql_operator.v2',
    default_args=default_args,
    start_date=datetime(2024, 5, 23),
    schedule_interval='0 0 * * *'
) as dag:
    task1 = PostgresOperator(
        task_id = 'create_table',
        postgres_conn_id='airflow_postgres_test',
        sql="""
            CREATE TABLE IF NOT EXISTS DAG_RUNS (
                dt date,
                dag_id CHARACTER VARYING,
                PRIMARY KEY (dt, dag_id)
            )
        """
    )
    
    task2 = PostgresOperator(
        task_id = "delete_from_table",
        postgres_conn_id="airflow_postgres_test",
        sql="""
            delete from dag_runs where dt = '{{ds}}' and dag_id = '{{dag.dag_id}}'
        """
    )
    
    task3 = PostgresOperator(
        task_id = 'insert_into_table',
        postgres_conn_id='airflow_postgres_test',
        sql="""
            INSERT INTO DAG_RUNS(dt, dag_id) VALUES('{{ds}}', '{{dag.dag_id}}')
        """
    )
    
    task1 >> task2 >> task3
    
    