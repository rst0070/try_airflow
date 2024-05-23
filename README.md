## Execute airflow with docker compose
  
__CeleryExecutor to LocalExecutor__  
For simplicity, set the `x-airflow-common:environment:AIRFLOW__CORE__EXECUTOR` as LocalExecutor rather then Celery Executor. 
So that, we dont need `x-airflow-common:environment:AIRFLOW__CELERY__RESULT_BACKEND` and `x-airflow-common:environment:AIRFLOW__CELERY__BROKER_URL` settings. 
In the setting, redis is needed by celery, thus we can remove that(`x-airflow-common:depends_on:redis`, `services:redis`).
And remove `services:airflow-worker` and `services:flower`.  
  
  
__Setting the right Airflow user__  
```sh
mkdir -p ./dags ./logs ./plugins ./config
echo -e "AIRFLOW_UID=$(id -u)" > .env
```  
  
__Initialize the database__  
downloading necessary images using default username and passwd(airflow:airflow)  
```sh
docker compose up airflow-init
```
If you add parameter(`-d`) then the docker containers will be operating background.  
  
__run__  
```
docker compose up -d
```
  
__Access the UI__  
default settings are below.  
- web addr - `localhost:8080`
- username - `airflow` 
- passwd - `airflow`
  
there are bunch of examples of DAG. you can click the DAG, unpause and trigger or refresh to see whats going on.  
  
  
__Remove examples__  
Below command will shut down containers ,and remove volumes defined in the yaml file.  
```
docker compose down -v
```
In the docker-compose.yaml, set `x-airflow-common:environment:AIRFLOW__CORE__LOAD_EXAMPLES` as false.  
```
docker compose up airflow-init
docker compose up -d
```
  
## Basic concept

## Task life cycle

## basic architecture

## DAG with Bash Operator
just make a python file including below code in `dag` directory.  
If you check the airflow web app after that, you would see the new dag
```python
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
    
```

## DAG python operator
just use different operator
```python
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
```

## XCOM - passing small parameters


## TASK Flow API - simplify the code using annotation

## Catch-up and backfill

## Connect to PostgreSQL  
__in the yaml__  
- set property `services:postgres:ports` as `5432:5432`
- re-start the service by command `docker compose up -d --no-deps --build postgres`  
  
after above things, you can just connect to the database with other tools  

