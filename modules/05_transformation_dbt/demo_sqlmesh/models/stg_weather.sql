MODEL (
  name weather.stg_weather,
  kind VIEW,
  grain (store_id, weather_date),
  description 'Погода магазина за день: одна строка на магазин и дату'
);

SELECT DISTINCT
  store_id,
  city_id,
  dt::DATE AS weather_date,
  precpt AS precipitation, -- осадки за день (precpt в датасете)
  avg_temperature
FROM read_parquet('/workspace/data/raw/freshretailnet_50k/data/*.parquet')
