MODEL (
  name weather.city_weather_daily,
  kind INCREMENTAL_BY_TIME_RANGE (
    time_column weather_date   -- SQLMesh сам подставит интервал в @start_date / @end_date
  ),
  cron '@daily',
  grain (city_id, weather_date),
  audits (
    not_null(columns := (city_id, weather_date)),
    unique_combination_of_columns(columns := (city_id, weather_date))
  ),
  description 'Погода города за день'
);

SELECT
  city_id,
  weather_date,
  AVG(precipitation) AS precipitation,
  AVG(avg_temperature) AS avg_temperature,
  COUNT(*) AS stores
FROM weather.stg_weather
WHERE weather_date BETWEEN @start_date AND @end_date
GROUP BY city_id, weather_date
