from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator

default_args = {
    'owner'         : 'rst0070',
    'retries'       : 5,
    'retry_delay'   : timedelta(minutes=2)
}

with DAG(
    dag_id = 'first_dag_v3',
    default_args=default_args,
    description= 'My first airflow dag',
    start_date = datetime(2024, 5, 22),
    schedule_interval='@daily'
) as dag:
    
    task1 = BashOperator(
        task_id = 'task1',
        bash_command='echo Hello world, this is my first task!'
    )
    
    task2 = BashOperator(
        task_id = 'task2',
        bash_command='echo This is my second task! this will be executed after task1'
    )
    
    task3 = BashOperator(
        task_id = 'task3',
        bash_command='echo This is my third task! this will be executed after task1 and parallel as task2'
    )
    
    ##
    ## dependency method 1
    ##
    # task1.set_downstream(task2)
    # task1.set_downstream(task3)
    ##
    ## dependency method 2
    ##
    # task1.set_downstream([task2, task3])
    ##
    ## dependency method 3
    ##
    # task1 >> task2
    # task1 >> task3
    ##
    ## dependency method 4
    ##
    task1 >> [task2, task3]
    
    