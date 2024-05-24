## 1. Execute airflow with docker compose
  
### 1.1 Simplify: CeleryExecutor to LocalExecutor
For simplicity, use LocalExecutor. To do that, we need to modify `docker-compose.yaml` file.  
- change the `x-airflow-common:environment:AIRFLOW__CORE__EXECUTOR` to `LocalExecutor` from `Celery Executor`.  

Now, we don't need some settings, so remove below elements.   
- `x-airflow-common:environment:AIRFLOW__CELERY__RESULT_BACKEND`
- `x-airflow-common:environment:AIRFLOW__CELERY__BROKER_URL`
- `x-airflow-common:depends_on:redis` and `services:redis`
    - In the setting, redis is needed by celery
- `services:airflow-worker` and `services:flower`  
  
### 1.2 Setting the right Airflow user__  
```sh
mkdir -p ./dags ./logs ./plugins ./config
echo -e "AIRFLOW_UID=$(id -u)" > .env
```  
  
### 1.3 Run
__Initialize the database__  
downloading necessary images using default username and passwd(airflow:airflow)  
```sh
docker compose up airflow-init
```    
__Run__  
If you add parameter(`-d`) then the docker containers will be operating background.  
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
In the docker-compose.yaml, set `x-airflow-common:environment:AIRFLOW__CORE__LOAD_EXAMPLES` as false, 
and just run the containers again.  
  
## 2. Basic concept

## 3. Task life cycle

## 4. Basic architecture of Airflow

## 5. DAG with Bash Operator
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

## 6. DAG python operator
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

## 7. XCOM - passing small parameters


## 8. TASK Flow API - simplify the code using annotation

## 9. Catch-up and backfill

## 10. Connect to PostgreSQL  
__in the yaml__  
- set property `services:postgres:ports` as `5432:5432`
- re-start the service by command `docker compose up -d --no-deps --build postgres`  
  
after above things, you can just connect to the database with other tools  

## 11. Install Python packages using docker -  Extend image
__1. set requirements__  
with requirements.txt like below.
```
scikit-learn==0.24.2
```
__2. define extended docker image__  
create Dockerfile like below.  
```Dockerfile
FROM apache/airflow:<version of the airflow>
COPY requirements.txt /requirements.txt
RUN pip install --user --upgrade pip
RUN pip install --no-cache-dir --user -r /requirements.txt
```  
  
__3. Build the extended image__  
using below commends.  
```sh
docker build . --tag extending_airflow:latest
```
  
__4. Import the extended image to docker-compose.yaml__  
From the docker-compose.yaml file, change `x-airflow-common:image` as `${AIRFLOW_IMAGE_NAME:-extending_airflow:latest}`  
  
__5. Run__  

## 12. Sensor operator with AWS S3
__What is Sensor?__  
Sensor is a special type of operator waits for something to occur. 
For example, waiting for producer to make data file.  
  
__Substitute for AWS S3: MINIO__  
MINIO is compatable api with AWS S3 and opensource.