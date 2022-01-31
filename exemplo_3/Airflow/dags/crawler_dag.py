import re
import requests

from bs4 import BeautifulSoup
from pathlib import Path
from unidecode import unidecode

from airflow import DAG
from datetime import datetime
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.bash_operator import BashOperator
from airflow.contrib.sensors.file_sensor import FileSensor
from airflow.operators.python_operator import PythonOperator

def crawler_cripto_cotacao():
    headers = requests.utils.default_headers()
    headers.update({
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0',
    })

    path_csv = f'/usr/local/airflow/datalake/raw/crawler/year={datetime.now().year}/month={datetime.now().month}/day={datetime.now().day}'
    mkdir_path = Path(path_csv)
    mkdir_path.mkdir(parents=True,exist_ok=True)

    page = requests.get('https://br.investing.com/crypto/', headers=headers)
    soup = BeautifulSoup(page.text, 'html.parser')
    
    cripto_table = soup.find('table', attrs={'class','genTbl js-top-crypto-table mostActiveStockTbl crossRatesTbl allCryptoTlb wideTbl elpTbl elp15'})
    cripto_table_head = cripto_table.find('thead')
    cols_names = cripto_table_head.find_all('th')
    header_line = ''
    for col in cols_names[1:]:
        header_line += re.sub(r'[^\w\s]','',(unidecode(col.text.strip()).lower())).replace(' ','_') + ','

    f = open(path_csv+'/crawler_result.csv', 'w')
    f.write(header_line[:-1])
    f.write("\n")

    cripto_table_body = cripto_table.find('tbody')
    rows = cripto_table_body.find_all('tr')
    for row in rows:
        cols = row.find_all('td')
        cols = [(ele.text.strip()).replace(',','.') for ele in cols]
        write_row = ','.join(cols[1:])
        f.write(write_row)
        f.write("\n")
    f.close()

with DAG(
    'minha_quarta_dag',
    description= 'Minha Quarta DAG',
    schedule_interval='@once',
    start_date=datetime(2022,1,1),
    catchup = False
) as dag:
    task_1 = DummyOperator(task_id='faz_algo')
    task_2 = DummyOperator(task_id='faz_outra_coisa')
    task_3 = BashOperator(task_id='bash_task',bash_command= "echo 'Treinamento Data engineer 101 - Dell Lead'")
    task_4 = FileSensor(task_id ='sensor_de_texto', fs_conn_id="my_fs_conn", timeout= 30*60, poke_interval=1*60, filepath= 'text.txt')
    task_5 = PythonOperator(task_id='crawler_cript', python_callable=crawler_cripto_cotacao)
    
    task_1 >> task_4 >> task_5 >>task_3 >> task_2