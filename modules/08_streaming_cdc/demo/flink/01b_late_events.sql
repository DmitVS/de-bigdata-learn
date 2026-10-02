-- Демо модуля 08, урок 04, шаг 4: опоздавшие события и оконный агрегат.
-- Топик demo.weather_late — одна партиция: watermark источника равен watermark этой партиции.
-- (На нескольких партициях watermark — минимум по ним, и при быстром переигрывании одна партиция
-- может быть прочитана целиком раньше, чем сдвинутся остальные, — опоздание не проявится.)
-- Watermark выпускается на каждом событии (on-event), а не раз в 200 мс: иначе весь топик
-- прочитается между двумя выпусками.

SET 'sql-client.execution.result-mode' = 'tableau';
SET 'parallelism.default' = '1';

CREATE TEMPORARY TABLE weather_late (
    store_id BIGINT,
    city_id BIGINT,
    event_time TIMESTAMP(3),
    precipitation DOUBLE,
    temperature DOUBLE,
    WATERMARK FOR event_time AS event_time - INTERVAL '1' HOUR
) WITH (
    'connector' = 'kafka',
    'topic' = 'demo.weather_late',
    'properties.bootstrap.servers' = 'redpanda:9092',
    'scan.startup.mode' = 'earliest-offset',
    'scan.bounded.mode' = 'latest-offset',
    'scan.watermark.emit.strategy' = 'on-event',
    'format' = 'json',
    'json.timestamp-format.standard' = 'SQL'
);

SELECT window_start, city_id, count(*) AS readings
FROM TABLE(TUMBLE(TABLE weather_late, DESCRIPTOR(event_time), INTERVAL '1' DAY))
WHERE city_id IN (0, 1)
GROUP BY window_start, window_end, city_id;
