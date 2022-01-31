from airflow import DAG
from datetime import datetime
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.bash_operator import BashOperator


with DAG(
    'minha_segunda_dag',
    description= 'Minha segunda DAG',
    schedule_interval='@once',
    start_date=datetime(2022,1,1),
    catchup = False
) as dag:
    task_1 = DummyOperator(task_id='faz_algo')
    task_2 = DummyOperator(task_id='faz_outra_coisa')
    task_3 = BashOperator(task_id='bash_task',bash_command= "echo 'Treinamento Data engineer 101 - Dell Lead'")

    task_1 >> task_3 >>task_2