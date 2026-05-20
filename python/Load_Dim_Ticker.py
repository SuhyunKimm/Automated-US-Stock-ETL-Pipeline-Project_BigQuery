import finnhub
import pandas as pd
import numpy as np
import pyodbc
import os
from google.cloud import bigquery
from pathlib import Path

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r"C:\Users\Suhyun\Desktop\Projects\Automated-US-Stock-ETL-Pipeline-Project_BigQuery\keys\key.json"

BASE_DIR = Path.cwd()
file_path = BASE_DIR / "keys" / "Finnhub_key.txt"
finnhub_key = ""
with open(file_path) as f:
    line = f.readline()
    if line and line != "" :
        finnhub_key = line

finnhub_client = finnhub.Client(api_key=finnhub_key)


tickers = ["AMD", "NVDA", "AMZN", "PLTR", "TSLA", "AAPL"]
profile = []

for t in tickers :
    data = finnhub_client.company_profile2(symbol=t)
    if data :
        profile.append(data)

df = pd.DataFrame(profile)

df = df[['ticker', 'name', 'country', 'finnhubIndustry', 'exchange', 'currency']]
df.rename(columns = 
    {'name' : 'companyName', 
    'finnhubIndustry' : 'industry', 
    'exchange' : 'market'},
    inplace = True)

# BigQuery client
client = bigquery.Client(project='us-stock-etl-pipeline')
table_id = 'us-stock-etl-pipeline.us_stock.bronze_tickers'

# load data into BigQuery
job_config = bigquery.LoadJobConfig(
    write_disposition='WRITE_APPEND'
)

job = client.load_table_from_dataframe(
    df,
    table_id,
    job_config = job_config
)

job.result()

f.close()