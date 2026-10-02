-- Песочница CDC (модуль 08, урок 03): настройки городов — маленькая таблица, изменения которой
-- Debezium превращает в события. Создаётся в отдельной базе sandbox_cdc, в конце урока удаляется.
CREATE TABLE city_settings (
    city_id bigint PRIMARY KEY,
    rain_threshold double precision NOT NULL DEFAULT 1.0,
    status text NOT NULL DEFAULT 'active',
    updated_at timestamptz NOT NULL DEFAULT now()
);

INSERT INTO city_settings (city_id)
SELECT g FROM generate_series(0, 17) AS g;  -- 18 городов датасета
