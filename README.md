# Try Airflow  
This is my code trying to grasp concept of Apache Airflow, and below is the description.  
I learned it from [coder2j's youtube video](https://youtu.be/K9AnJ9_ZAXE?si=BnTtx4wbdwvpSHdB).  

1. [Execution of Airflow](#1-execute-airflow-with-docker-compose)
2. [Basic concepts](#2-basic-concepts-of-airflow)
3. [Implement DAGs](#3-implement-dags)
4. [XCOM](#4-xcom---passing-small-parameters)
5. [Task Flow API](#5-task-flow-api---simplify-the-code-using-annotation)
6. [Catch-up and Backfill](#6-catch-up-and-backfill)
7. [Schedule with Cron Expression](#7-schedule-with-cron-expression)
8. [Connect to PostgreSQL](#8-connect-to-postgresql)
9. [Install Python Packages](#9-install-python-packages-using-docker----extend-image)
10. [Sensor Operator with AWS S3](#10-sensor-operator-with-aws-s3)
  
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
  
## 2. Basic Concepts of Airflow

### 2.1. Basic Architecture and Concepts
__What is Airflow?__  
Airflow does workflow management.  
A Workflow is represented as a *DAG*(Directed Acyclic Graph) of tasks in Airflow.  
*Task* is an *Operator* which is defined by airflow or customized by user. 
The Operator does jobs specified by author of the code.  
  
__Execution Date, DAG Run and Task Instance__  
- DAG run(=Instance) = executed DAG = Defined DAG + Execution date
- Task Instance = executed Task = Defined Task + Execution date  
    
__Basic Architecture__  
<img src="https://airflow.apache.org/docs/apache-airflow/stable/_images/diagram_basic_airflow_architecture.png" width="700" />  
Check the detailed concepts [here](https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/overview.html)    

### 2.2. Task life cycle
<img src="https://airflow.apache.org/docs/apache-airflow/stable/_images/task_lifecycle_diagram.png"  width="700" style="background-color: white;"/>  

Check the detailed concepts [here](https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/tasks.html)  

## 3. Implement DAGs
Creating a python file including implementation of DAG in `dag` directory is needed.  
After that, you can check the created dag on airflow web app.  

### 3.1. Using BashOperator
End of this example code, you can see how to set dependencies between Tasks.  
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
### 3.2. DAG python operator
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

## 4. XCOM - passing small parameters
Using XCOM, we can push and pull some values. However, it is only for small data!  (MAX size of it is 48KB)  
__Access XCOM__  
When we use a python function as `PythonOperator`, we can get `airflow.models.taskinstance.TaskInstance` instance by defining parameter of the function by `ti`. 
With the parameter,
- `ti.xcom_pull(...)` - get value using task id and key
- `ti.xcom_push(...)` - push a value using key  
  
__Example DAG__  
```python
from datetime import datetime
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
```

## 5. TASK Flow API - simplify the code using annotation
From `airflow.decorators`, we can get annotations for defining DAGs and Tasks.  
Dependencies between tasks are automatically calculated. However, be careful about using returned values between tasks, because it uses XCOM.  
__Example code__  
```python
from airflow.decorators import dag, task
from datetime import datetime, timedelta

@dag(
    dag_id='dag_d_task_flow_api',
    description='',
    start_date=datetime(2024, 5, 24),
    schedule_interval='@daily'
)
def dag_func():
    
    @task()
    def print_msgs(msg1, msg2):
        print(f'{msg1}, {msg2}')
    
    @task()
    def get_msg1():
        return 'This is msg1'
    
    @task(multiple_outputs=True)
    def get_msg2():
        return {
            'msg1' : 'This is',
            'msg2' : 'msg2'
        }
    
    ## Task flow api calculates dependencies automatically
    ##
    m1 = get_msg1()
    m2 = get_msg2()
    
    print_msgs(msg1=m1, msg2=f"{m2['msg1']}{m2['msg2']}")

## Need to instanciate the dag
task_flow_dag = dag_func()
```
## 6. Catch-up and backfill
Catch-up and Backfill provide a way to run a dag using previous dates.  
   
__Catch up__  
Set `catchup = True` when defining DAG.  
  
__Backfill__  
In the terminal of airflow docker container, run the below command.  
```sh
airflow dags backfill -s <start_date> -e <end_date> <dag_id>
```  
## 7. Schedule with Cron Expression
Check [the airflow doc](https://airflow.apache.org/docs/apache-airflow/stable/authoring-and-scheduling/cron.html)  

## 8. Connect to PostgreSQL  
__Setting in the yaml__  
- set property `services:postgres:ports` as `5432:5432`
- re-start the service by command `docker compose up -d --no-deps --build postgres`  
  
__Connect with Airflow connection__   
From Airflow's Web UI, you can make postgres connection (Admin > connections) using following default values.  
- host - `host.docker.internal`, but using docker container's ip addr directly worked in my env.
  
__PostgresOperator__  
Using `airflow.providers.postgres.operators.postgres.PostgresOperator`, you can run sql.  
  
__Example code__  
```python
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
```

## 9. Install Python packages using docker -  Extend image
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

## 10. Sensor operator with AWS S3
__What is Sensor?__  
Sensor is a special type of operator waits for something to occur. 
For example, waiting for producer to make data file.  
  
__Substitute for AWS S3: MINIO__  
MINIO is compatable api with AWS S3 and opensource.