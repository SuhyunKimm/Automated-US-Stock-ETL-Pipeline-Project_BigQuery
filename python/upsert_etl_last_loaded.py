from google.cloud import bigquery
import pandas as pd

def upsert_etl_last_loaded(table_name: str, last_loaded_date) :
    client = bigquery.Client(project='us-stock-etl-pipeline')

    merge_query = f"""
        MERGE `us-stock-etl-pipeline.us_stock.etl_last_loaded` T
        USING (SELECT '{table_name}' AS tableName, DATE('{last_loaded_date}') AS lastLoadedDate) S
        ON T.tableName = S.tableName
        WHEN MATCHED THEN
        UPDATE SET lastLoadedDate = S.lastLoadedDate
        WHEN NOT MATCHED THEN
        INSERT (tableName, lastLoadedDate)
        VALUES(S.tableName, S.lastLoadedDate)
    """
    client.query(merge_query).result()