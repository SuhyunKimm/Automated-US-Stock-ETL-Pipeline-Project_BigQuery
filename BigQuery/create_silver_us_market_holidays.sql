-- create us_market_holidays table for silver layer

create or replace table `us-stock-etl-pipeline.us_stock.silver_us_market_holidays`
partition by date
as
select
  date(date) as date,
  lower(status) as status,
  case
    when startTime is not null then timestamp(datetime(date, startTime))
  end as startTime,
  case
    when endTime is not null then timestamp(datetime(date, endTime))
  end as endTime,
  description,
  current_timestamp() as ingestedAt
from (
  select 
    *,
    row_number() over (
      partition by date, description
      order by date
    ) as rn
  from `us-stock-etl-pipeline.us_stock.bronze_us_market_holidays`
)
where 
  rn = 1
  and date is not null;