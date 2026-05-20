-- create dim_ticker table for analytics layer

create or replace table `us-stock-etl-pipeline.us_stock.dim_ticker`
as
select
  upper(trim(ticker)) as ticker,
  companyName as company_name,
  country,
  industry,
  market,
  upper(trim(currency)) as currency,
  current_timestamp() as ingestedAt
from (
  select 
    *,
    row_number() over (
      partition by ticker
      order by ingestedAt desc
    ) as rn
  from `us-stock-etl-pipeline.us_stock.bronze_tickers`
)
where 
  rn = 1
  and ticker is not null
  and companyName is not null;