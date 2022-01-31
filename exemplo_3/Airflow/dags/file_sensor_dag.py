from socket import timeout
from airflow import DAG
from datetime import datetime
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.bash_operator import BashOperator
from airflow.contrib.sensors.file_sensor import FileSensor


with DAG(
    'minha_terceira_dag',
    description= 'Minha terceira DAG',
    schedule_interval='@once',
    start_date=datetime(2022,1,1),
    catchup = False
) as dag:
    task_1 = DummyOperator(task_id='faz_algo')
    task_2 = DummyOperator(task_id='faz_outra_coisa')
    task_3 = BashOperator(task_id='bash_task',bash_command= "echo 'Treinamento Data engineer 101 - Dell Lead'")
    task_4 = FileSensor(task_id ='sensor_de_texto', fs_conn_id="my_fs_conn", timeout= 30*60, poke_interval=1*60, filepath= 'text.txt')
    task_1 >> task_4>> task_3 >> task_2