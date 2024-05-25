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