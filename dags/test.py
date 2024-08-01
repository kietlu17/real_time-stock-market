from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime

default_args = {
    'owner' : 'airflow',
    'start_date' : datetime(2024, 7, 10),
}

dag = DAG(dag_id='test', 
        default_args=default_args, 
        schedule_interval='*/2 * * * *', 
        catchup=False
    )

def print_hello():
    print('Hello world!')

def end():
    print('End')

hello_operator = PythonOperator(
    task_id='hello_task',
    python_callable=print_hello,
    dag=dag
)

end_operator = PythonOperator(
    task_id='end_task',
    python_callable=end,
    dag=dag
)

hello_operator >> end_operator