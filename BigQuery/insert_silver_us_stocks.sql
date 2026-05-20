-- create us_stocks table for silver layer

create or replace table `us-stock-etl-pipeline.us_stock.silver_us_stocks`
partition by date
as
select
  upper(trim(ticker)) as ticker,
  date(date) as date,
  round(cast(open as numeric),6) as open,
  round(cast(high as numeric),6) as high,
  round(cast(low as numeric),6) as low,
  round(cast(close as numeric),6) as close,
  cast(volume as int64) as volume,
  current_timestamp() as ingestedAt
from (
  select 
    *,
    row_number() over (
      partition by ticker, date
      order by ingestedAt
    ) as rn
  from `us-stock-etl-pipeline.us_stock.bronze_us_stocks`
)
where 
  rn = 1
  and ticker is not null
  and date is not null;