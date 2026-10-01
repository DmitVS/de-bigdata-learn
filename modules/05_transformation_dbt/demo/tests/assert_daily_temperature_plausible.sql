-- Сингулярный тест: средняя температура города за день в правдоподобных пределах.
-- Пороги — переменные, чтобы их можно было ужесточить: --vars '{max_temp: 30}'
{{ config(severity='error', store_failures=true) }}
select city_id, weather_date, avg_temperature
from {{ ref('int_city_weather_daily') }}
where avg_temperature not between {{ var('min_temp', -40) }} and {{ var('max_temp', 50) }}
