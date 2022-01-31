import csv
import random
import re
import requests
import pandas as pd
import pymongo

from bs4 import BeautifulSoup
from pathlib import Path
from unidecode import unidecode

from airflow import DAG
from datetime import datetime

from airflow.operators.python_operator import PythonOperator
from airflow.operators.dummy_operator import DummyOperator
from airflow.hooks.postgres_hook import PostgresHook


user_agent_list = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36',
    'Mozilla/5.0 (Windows NT 5.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
    'Mozilla/4.0 (compatible; MSIE 9.0; Windows NT 6.1)',
    'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0)',
    'Mozilla/5.0 (Windows NT 6.1; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (Windows NT 6.2; WOW64; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.0; Trident/5.0)',
    'Mozilla/5.0 (Windows NT 6.3; WOW64; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0)',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0)',
    'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; Trident/6.0)',
    'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; .NET CLR 2.0.50727; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729)'
]

BASE_PATH = '/usr/local/airflow/datalake'
def create_current_day_folder(root_folder, layer):
    path_ingestion = Path(f'{BASE_PATH}/{layer}/{root_folder}/year={datetime.now().year}/month={datetime.now().month}/day={datetime.now().day}')
    path_ingestion.mkdir(parents=True, exist_ok=True)
    return f'{BASE_PATH}/{layer}/{root_folder}/year={datetime.now().year}/month={datetime.now().month}/day={datetime.now().day}'

def crawler_cripto_values():
    user_agent = random.choice(user_agent_list)
    headers = {'User-Agent': user_agent}
    path = create_current_day_folder('crawler','raw')
    page = requests.get('https://br.investing.com/crypto/',headers=headers)
    soup = BeautifulSoup(page.text, 'html.parser')

    cripto_table = soup.find('table', attrs={'class','genTbl js-top-crypto-table mostActiveStockTbl crossRatesTbl allCryptoTlb wideTbl elpTbl elp15'})
    cripto_table_head = cripto_table.find('thead')
    col_names = cripto_table_head.find_all('th')
    header_line = ''
    for col in col_names[1:]:
        header_line += re.sub(r'[^\w\s]','',(unidecode(col.text.strip()).lower())).replace(' ','_') + ','

    f = open(path+'/crawler_result.csv', 'w')
    f.write(header_line[:-1])
    f.write("\n")

    cripto_table_body = cripto_table.find('tbody')
    rows = cripto_table_body.find_all('tr')
    for row in rows:
        cols = row.find_all('td')
        cols = [(ele.text.strip()).replace('.','').replace(',','.') for ele in cols]
        write_row = ','.join(cols[1:])
        f.write(write_row)
        f.write("\n")
    f.close()

def get_api_data():
    req = requests.get('http://web:8082/listar_cripto_aportes')
    data = req.json()
    keys = data[0].keys()
    path = create_current_day_folder('api','raw')
    with open(path+'/api_results.csv', 'w', newline='') as f:
        dict_writer = csv.DictWriter(f, keys)
        dict_writer.writeheader()
        dict_writer.writerows(data)

def get_postgres_data():
    path = create_current_day_folder('postgres','raw')
    request = "SELECT * FROM treinamento_lead.users"
    pg_hook = PostgresHook(postgre_conn_id="postgre_default")
    conn = pg_hook.get_conn()
    cursor = conn.cursor()
    cursor.execute(request)
    users = cursor.fetchall()
    with open(path + '/postgres_result.csv', 'w') as f:
        f.write('id,nome,sobrenome')
        f.write("\n")
        for user in users:
            write_row = f'{user[0]},{user[1]},{user[2]}'
            f.write(write_row)
            f.write("\n")

def clean_postgres_data():
    df = pd.read_csv(f'{BASE_PATH}/raw/postgres/year={datetime.now().year}/month={datetime.now().month}/day={datetime.now().day}/postgres_result.csv')
    df_renamed = df.rename(columns= {"nome":"name","sobrenome":"last_name"})
    path = create_current_day_folder('postgres','refined')
    df_renamed.to_csv(path+'/postgres_result_refined.csv', index=False,header=True, decimal='.',float_format='%.2f')

def clean_api_data():
    df = pd.read_csv(f'{BASE_PATH}/raw/api/year={datetime.now().year}/month={datetime.now().month}/day={datetime.now().day}/api_results.csv')
    df_renamed = df.rename(columns= {"valor_do_aporte":"value"})
    df_filtered = df_renamed.drop(['id'], axis =1)
    path = create_current_day_folder('api','refined')
    df_filtered.to_csv(path+'/api_results_refined.csv', index=False,header=True, decimal='.',float_format='%.2f')

def clean_crawlers_data():
    df = pd.read_csv(f'{BASE_PATH}/raw/crawler/year={datetime.now().year}/month={datetime.now().month}/day={datetime.now().day}/crawler_result.csv')
    df_renamed = df.rename(columns={'nome':'cripto_name','codigo':'cripto_code','preco_usd':'price_usd',})
    df_filtered = df_renamed.drop(['capitalizacao','vol_24h','vol_total','var_24h','var_7d'], axis= 1)
    path = create_current_day_folder('crawler','refined')
    df_filtered.to_csv(path+'/crawler_result_refined.csv', index=False,header=True, decimal='.',float_format='%.2f')

def create_refined_table():
    df_api = pd.read_csv(f'{BASE_PATH}/refined/api/year={datetime.now().year}/month={datetime.now().month}/day={datetime.now().day}/api_results_refined.csv')
    df_postgres = pd.read_csv(f'{BASE_PATH}/refined/postgres/year={datetime.now().year}/month={datetime.now().month}/day={datetime.now().day}/postgres_result_refined.csv')
    df_merge_api_postgres = pd.merge(df_api,df_postgres, left_on='user_id', right_on='id')
    df_crawler = pd.read_csv(f'{BASE_PATH}/refined/crawler/year={datetime.now().year}/month={datetime.now().month}/day={datetime.now().day}/crawler_result_refined.csv')
    df_merge = pd.merge(df_merge_api_postgres, df_crawler, left_on='cripto', right_on='cripto_name')
    df_merge['quantity_purchased'] = df_merge['value'] / df_merge['price_usd']
    df_droped = df_merge.drop(['cripto_code','cripto','id'], axis=1)
    df_final = df_droped[['user_id','name','last_name','cripto_name','price_usd','value','quantity_purchased']]
    path = create_current_day_folder('dw_lead','trusted')
    df_final.to_csv(path+'/purchase_analysis.csv', index=False,header=True, decimal='.',float_format='%.10f')

def insert_into_dw():
    myclient = pymongo.MongoClient("mongodb://root:lead@mongo:27017")
    mydb = myclient["dw_lead"]
    mycol = mydb["purchase_analysis"]
    df = pd.read_csv(f'{BASE_PATH}/trusted/dw_lead/year={datetime.now().year}/month={datetime.now().month}/day={datetime.now().day}/purchase_analysis.csv')
    lst_value = df.to_dict('records')
    _ids = mycol.insert_many(lst_value)
    print(_ids.inserted_ids)

with DAG(
    'pipeline_end_to_end',
    schedule_interval='@once',
    start_date=datetime(2022,1,1),
    catchup = False
) as dag:

    crawler_ingestion = PythonOperator(task_id='crawler_cript', python_callable=crawler_cripto_values)
    api_ingestion = PythonOperator(task_id='consumo_api', python_callable=get_api_data)
    postgres_ingestion = PythonOperator(task_id='consumo_postgres', python_callable=get_postgres_data)
    
    clean_postgres_data = PythonOperator(task_id = 'refined_postgres', python_callable=clean_postgres_data)
    clean_api_data = PythonOperator(task_id = 'refined_api', python_callable=clean_api_data)
    clean_crawlers_data = PythonOperator(task_id = 'refined_crawlers', python_callable=clean_crawlers_data)

    trusted_data = PythonOperator(task_id = 'trusted_table', python_callable=create_refined_table)

    dw_insert = PythonOperator(task_id = 'dw_insert', python_callable=insert_into_dw)
    dummy = DummyOperator(task_id='finalizando_pipeline')

    crawler_ingestion >> clean_crawlers_data >> trusted_data
    api_ingestion >> clean_api_data >> trusted_data
    postgres_ingestion >> clean_postgres_data >> trusted_data

    trusted_data >> dw_insert >> dummy