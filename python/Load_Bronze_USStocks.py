import pandas as pd
import yfinance as yf
from google.cloud import bigquery
import upsert_etl_last_loaded
from datetime import datetime, timedelta
import os

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r"C:\Users\Suhyun\Desktop\Projects\Automated-US-Stock-ETL-Pipeline-Project_BigQuery\keys\key.json"

client = bigquery.Client(project = 'us-stock-etl-pipeline')

# get last loaded ate for us stocks
query = """
    select lastLoadedDate
    from `us-stock-etl-pipeline.us_stock.etl_last_loaded`
    where tableName = 'us_stocks'
"""

result = client.query(query).result()
rows = list(result)

if rows :
    last_loaded_date = rows[0].last_loaded_date
else :
    last_loaded_date = None

# set the start date for our market data request
start_date = datetime(year=2021, month=1, day=1).date()

if last_loaded_date != None and last_loaded_date != -1:
    start_date = last_loaded_date + timedelta(days=1)
# Define interval for fetching data
interval = "1d"

# Define tickers in a list
tickers = ["AMD", "NVDA", "AMZN", "PLTR", "TSLA", "AAPL"]

# fetch data from yfinance
data = yf.download(tickers, start=start_date, interval=interval, progress=False)

df = data.stack(level=1, future_stack=True).reset_index()
df = df[pd.to_datetime(df['Date']).dt.date >= start_date]

if df.empty :
    exit()

df.columns = ['Date', 'Ticker', 'Open', 'High', 'Low', 'Close', 'Volume']
df = df[['Ticker', 'Date', 'Open', 'High', 'Low', 'Close', 'Volume']]

df['Date'] = pd.to_datetime(df['Date']).dt.date
df['Open'] = pd.to_numeric(df['Open'], errors='coerce')
df['High'] = pd.to_numeric(df['High'], errors='coerce')
df['Low'] = pd.to_numeric(df['Low'], errors='coerce')
df['Close'] = pd.to_numeric(df['Close'], errors='coerce')
df['Volume'] = pd.to_numeric(df['Volume'], errors='coerce')

df = df.dropna(subset=['Ticker', 'Date', 'Close'])
most_recent_date = max(df['Date'])

table_id = 'us-stock-etl-pipeline.us_stock.bronze_us_stocks'

# load data into BigQuery
job_config = bigquery.LoadJobConfig(
    write_disposition='WRITE_APPEND'
)
job = client.load_table_from_dataframe(df, table_id, job_config=job_config)
job.result()

# update etl_last_loaded
upsert_etl_last_loaded.upsert_etl_last_loaded("us_stocks", most_recent_date)