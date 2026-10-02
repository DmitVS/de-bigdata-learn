-- Демо модуля 08, урок 05: потоковая запись дневных окон в Iceberg через REST-каталог Lakekeeper.
-- Запуск: make flink-sql ARGS="-f /workspace/modules/08_streaming_cdc/demo/flink/02_weather_to_iceberg.sql"
-- Запись фиксируется в Iceberg на каждом чекпоинте (execution.checkpointing.interval = 10 с).

SET 'parallelism.default' = '1';

CREATE TEMPORARY TABLE weather_readings (
    store_id BIGINT,
    city_id BIGINT,
    event_time TIMESTAMP(3),
    precipitation DOUBLE,
    temperature DOUBLE,
    WATERMARK FOR event_time AS event_time - INTERVAL '1' HOUR
) WITH (
    'connector' = 'kafka',
    'topic' = 'demo.weather_readings',
    'properties.bootstrap.servers' = 'redpanda:9092',
    'properties.group.id' = 'flink-weather-to-iceberg',
    'scan.startup.mode' = 'earliest-offset',
    'format' = 'json',
    'json.timestamp-format.standard' = 'SQL'
);

CREATE CATALOG lh WITH (
    'type' = 'iceberg',
    'catalog-type' = 'rest',
    'uri' = 'http://lakekeeper:8181/catalog',
    'warehouse' = 'lakehouse',
    'header.X-Iceberg-Access-Delegation' = 'vended-credentials',
    'io-impl' = 'org.apache.iceberg.aws.s3.S3FileIO'
);

CREATE DATABASE IF NOT EXISTS lh.sandbox_flink;

CREATE TABLE IF NOT EXISTS lh.sandbox_flink.city_weather_daily (
    window_start TIMESTAMP(3),
    city_id BIGINT,
    readings BIGINT,
    precipitation DOUBLE
);

-- Потоковый INSERT: задание живёт, пока его не остановят; каждое закрытое окно попадает в
-- таблицу на ближайшем чекпоинте.
INSERT INTO lh.sandbox_flink.city_weather_daily
SELECT window_start, city_id, count(*), round(avg(precipitation), 3)
FROM TABLE(TUMBLE(TABLE weather_readings, DESCRIPTOR(event_time), INTERVAL '1' DAY))
GROUP BY window_start, window_end, city_id;
