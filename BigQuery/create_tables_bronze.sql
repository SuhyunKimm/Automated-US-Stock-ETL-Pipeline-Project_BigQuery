-- create tables for bronze layer

create table if not exists `us-stock-etl-pipeline.us_stock.bronze_us_market_holidays` (
  date date not null,
  status string,
  startTime time,
  endTime time,
  description string,
  ingestedAt timestamp default current_timestamp()
)
partition by date;

create table if not exists `us-stock-etl-pipeline.us_stock.bronze_us_stocks` (
  ticker string, 
  date date,
  open float64,
  high float64,
  low float64,
  close float64,
  volume int64,
  ingestedAt timestamp default current_timestamp()
)
partition by date
cluster by ticker;

create table if not exists `us-stock-etl-pipeline.us_stock.bronze_tickers` (
  ticker string not null,
  companyName string,
  country string,
  industry string,
  market string,
  currency string,
  ingestedAt timestamp default current_timestamp()
);

create table if not exists `us-stock-etl-pipeline.us_stock.etl_last_loaded` (
  tableName string,
  lastLoadedDate date,
  updatedAt timestamp default current_timestamp()
);