
from airflow import DAG
from datetime import datetime
from airflow.operators.dummy_operator import DummyOperator

with DAG(
    'minha_primeira_dag',
    description= 'Minha primeira DAG',
    schedule_interval='@once',
    start_date=datetime(2022,1,1),
    catchup = False
) as dag:
    task_1 = DummyOperator(task_id='faz_algo')
    task_2 = DummyOperator(task_id='faz_outra_coisa')

    task_1 >> task_2