-- Демо модуля 08, урок 04: окна по времени события над потоком показаний погоды.
-- Запуск: make flink-sql ARGS="-f /workspace/modules/08_streaming_cdc/demo/flink/01_weather_windows.sql"
-- Источник ограничен текущим концом топика (scan.bounded.mode), поэтому запрос завершается.

SET 'sql-client.execution.result-mode' = 'tableau';
SET 'parallelism.default' = '1';

CREATE TEMPORARY TABLE weather_readings (
    store_id BIGINT,
    city_id BIGINT,
    event_time TIMESTAMP(3),
    precipitation DOUBLE,
    temperature DOUBLE,
    -- время события и допустимое опоздание: окно закрывается, когда watermark его прошёл
    WATERMARK FOR event_time AS event_time - INTERVAL '1' HOUR
) WITH (
    'connector' = 'kafka',
    'topic' = 'demo.weather_readings',
    'properties.bootstrap.servers' = 'redpanda:9092',
    'scan.startup.mode' = 'earliest-offset',
    'scan.bounded.mode' = 'latest-offset',
    'format' = 'json',
    'json.timestamp-format.standard' = 'SQL'
);

-- Дневное окно по городу: сколько магазинов прислали показание и средние осадки
SELECT window_start, city_id, count(*) AS readings, round(avg(precipitation), 3) AS precipitation
FROM TABLE(TUMBLE(TABLE weather_readings, DESCRIPTOR(event_time), INTERVAL '1' DAY))
WHERE city_id IN (0, 1)
GROUP BY window_start, window_end, city_id;
