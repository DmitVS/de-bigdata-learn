-- Дневная витрина продаж в ClickHouse из Iceberg (урок 03): каталог lake, загрузка в копию,
-- атомарная замена. Город и категория добавлены из справочников, чтобы дашборд не делал join.
-- Запуск: make ch ARGS="--queries-file modules/10_serving_bi/demo/clickhouse/02_sales_daily.sql"
SET allow_database_iceberg = 1;

CREATE DATABASE IF NOT EXISTS lake ENGINE = DataLakeCatalog('http://lakekeeper:8181/catalog')
SETTINGS catalog_type = 'rest', warehouse = 'lakehouse';

CREATE TABLE IF NOT EXISTS serving_demo.sales_daily
(
    dt                Date,
    city_id           UInt16,
    store_id          UInt16,
    first_category_id UInt16,
    product_id        UInt16,
    sale_amount       Float64,
    oos_hours         UInt8,
    discount          Float32,
    activity_flag     UInt8,
    holiday_flag      UInt8,
    precpt            Float32,
    avg_temperature   Float32
)
ENGINE = MergeTree
PARTITION BY toYYYYMM(dt)
ORDER BY (city_id, store_id, dt);

DROP TABLE IF EXISTS serving_demo.sales_daily_new;

CREATE TABLE serving_demo.sales_daily_new AS serving_demo.sales_daily;

INSERT INTO serving_demo.sales_daily_new
SELECT f.dt, s.city_id, f.store_id, p.first_category_id, f.product_id, f.sale_amount,
       f.oos_hours, f.discount, f.activity_flag, f.holiday_flag, f.precpt, f.avg_temperature
FROM lake.`serving_demo.fct_sales_daily` AS f
JOIN lake.`serving_demo.dim_store` AS s ON s.store_id = f.store_id
JOIN lake.`serving_demo.dim_product` AS p ON p.product_id = f.product_id;

EXCHANGE TABLES serving_demo.sales_daily AND serving_demo.sales_daily_new;

DROP TABLE serving_demo.sales_daily_new;

SELECT count() AS rows, round(sum(oos_hours) / (16 * count()), 4) AS oos_share
FROM serving_demo.sales_daily;
