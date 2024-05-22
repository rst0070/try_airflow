from airflow import DAG
from datetime import datetime, timedelta
from airflow.operators.python import PythonOperator

default_arg = {
    'owner'         : 'rst0070',
    'retries'       : 5,
    'retry_delay'   : timedelta(minutes=2)
}

def printFunc(message:str):
    print(message)

with DAG(
    default_args=default_arg,
    dag_id='b_python_operator',
    description='asdasd0',
    start_date=datetime(2024, 5, 21),
    schedule_interval='@daily'
) as  dag:
    
    task1 = PythonOperator(
        task_id = 'printFunc',
        python_callable=printFunc,
        op_kwargs={'message': 'Hello world!'}
    )