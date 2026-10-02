-- Демо модуля 08, урок 03: события Debezium как таблица изменений (changelog) во Flink.
-- Запуск: make flink-sql ARGS="-f /workspace/modules/08_streaming_cdc/demo/flink/03_cdc_changelog.sql"

SET 'sql-client.execution.result-mode' = 'tableau';
SET 'parallelism.default' = '1';

CREATE TEMPORARY TABLE city_settings (
    city_id BIGINT,
    rain_threshold DOUBLE,
    status STRING,
    PRIMARY KEY (city_id) NOT ENFORCED
) WITH (
    'connector' = 'kafka',
    'topic' = 'sandbox.public.city_settings',
    'properties.bootstrap.servers' = 'redpanda:9092',
    'scan.startup.mode' = 'earliest-offset',
    'scan.bounded.mode' = 'latest-offset',
    'format' = 'debezium-json'
);

-- Поток изменений превращается в текущее состояние: сколько городов в каждом статусе
SELECT status, count(*) AS cities FROM city_settings GROUP BY status;
