MODEL (
  name weather.city_rainy_days,
  kind FULL,
  grain city_id,
  description 'Дождливые дни и средняя температура по городам'
);

SELECT
  city_id,
  COUNT(*) AS days,
  COUNT(*) FILTER (WHERE precipitation >= 10.0) AS rainy_days,
  ROUND(AVG(avg_temperature), 2) AS avg_temperature
FROM weather.city_weather_daily
GROUP BY city_id
