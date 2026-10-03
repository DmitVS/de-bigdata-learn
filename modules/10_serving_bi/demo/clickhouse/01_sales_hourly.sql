-- Почасовые продажи в ClickHouse: 97 дней × 50 тыс. пар магазин–товар × 24 часа ≈ 116 млн строк.
-- Источник — файлы датасета: ARRAY JOIN разворачивает массивы hours_sale и hours_stock_status
-- в строки по часам. Запуск: make ch ARGS="--queries-file modules/10_serving_bi/demo/clickhouse/01_sales_hourly.sql"
CREATE DATABASE IF NOT EXISTS serving_demo;

DROP TABLE IF EXISTS serving_demo.sales_hourly;

CREATE TABLE serving_demo.sales_hourly
(
    dt                Date,
    hour              UInt8,
    city_id           UInt16,
    store_id          UInt16,
    product_id        UInt16,
    first_category_id UInt16,
    sale_amount       Float32,
    out_of_stock      UInt8,
    discount          Float32,
    activity_flag     UInt8
)
ENGINE = MergeTree
PARTITION BY toYYYYMM(dt)
ORDER BY (store_id, product_id, dt, hour);

INSERT INTO serving_demo.sales_hourly
SELECT
    toDate(dt),
    h - 1,
    city_id,
    store_id,
    product_id,
    first_category_id,
    hours_sale[h],
    hours_stock_status[h],
    discount,
    activity_flag
FROM file('raw/freshretailnet_50k/data/*.parquet', Parquet)
ARRAY JOIN arrayEnumerate(hours_sale) AS h;

OPTIMIZE TABLE serving_demo.sales_hourly FINAL;

SELECT count() AS rows, uniqExact(store_id) AS stores, min(dt), max(dt)
FROM serving_demo.sales_hourly;
