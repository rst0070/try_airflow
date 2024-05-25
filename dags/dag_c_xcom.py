from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.models.taskinstance import TaskInstance

def printFunc(ti:TaskInstance):
    """
    Using ti, we can access to xcoms data.
    """
    message = ti.xcom_pull(task_ids='message_generator', key='return_value')
    ext_msg = ti.xcom_pull(task_ids='message_generator', key='extra_msg')
    print(message, ext_msg)

def messageGenerator(ti:TaskInstance):
    """
    Using ti, we can push xcoms data.
    """
    ti.xcom_push(key='extra_msg', value='this is extra msg')
    return "This is returned message from messageGenerator and saved to xcom"

with DAG(
    dag_id='dag_c_xcoms_example',
    description='using xcoms',
    schedule_interval='@daily',
    start_date=datetime(2024, 5, 21),
) as dag:
    
    task1 = PythonOperator(
        task_id = 'print_func_task',
        python_callable = printFunc,
    )
    
    task2 = PythonOperator(
        task_id = 'message_generator',
        python_callable = messageGenerator
    )
    
    task2 >> task1