import pandas as pd
import numpy as np
from google.cloud import bigquery
from datetime import datetime
import upsert_etl_last_loaded
from pathlib import Path
import os

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r"C:\Users\Suhyun\Desktop\Projects\Automated-US-Stock-ETL-Pipeline-Project_BigQuery\keys\key.json"

BASE_DIR = Path.cwd()
file_path = BASE_DIR / "resources" / "nyse_holidays_latest.csv"

# load us market holidays data from csv file
df = pd.read_csv(file_path)
df = df[df['date'] >= '2021-01-01']
df = df[['date', 'status', 'start_time', 'end_time', 'holiday_name']]

# rename columns
df.rename(columns = {
    "date" : "date",
    "status" : "status",
    "start_time" : "startTime",
    "end_time" : "endTime",
    "holiday_name" : "description"},
    inplace = True)

df['date'] = pd.to_datetime(df['date']).dt.date

# get the start and end date of the data
start_date = min(df['date'])
end_date = max(df['date'])

# Convert time columns safely
df['startTime'] = pd.to_datetime(df['startTime'], format='%H:%M', errors='coerce').dt.time
df['endTime'] = pd.to_datetime(df['endTime'], format='%H:%M', errors='coerce').dt.time

# BigQuery client
client = bigquery.Client(project='us-stock-etl-pipeline')
table_id = 'us-stock-etl-pipeline.us_stock.bronze_us_market_holidays'

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

# update etl_last_loaded
upsert_etl_last_loaded.upsert_etl_last_loaded("us_market_holidays", end_date)