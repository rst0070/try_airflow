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

## Bash Operator
