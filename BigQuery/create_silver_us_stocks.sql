-- create us_stocks table for silver layer

create table if not exists `us-stock-etl-pipeline.us_stock.silver_us_stocks`
(
  ticker string not null,
  date date not null,
  open numeric,
  high numeric,
  low numeric,
  close numeric,
  volume int64,
  ingestedAt timestamp
)
partition by date
cluster by ticker;