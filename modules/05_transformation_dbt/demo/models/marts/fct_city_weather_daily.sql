{{
  config(
    materialized='incremental',
    incremental_strategy='delete+insert',
    unique_key=['city_id', 'weather_date'],
    on_schema_change='append_new_columns'
  )
}}
-- Город × день. При инкрементальном запуске пересчитываем последние N дней (окно перечитывания):
-- поздние данные за эти дни заменят старые строки по ключу.
select city_id, weather_date, precipitation, avg_temperature, stores
from {{ ref('int_city_weather_daily') }}
{% if is_incremental() %}
    where
        weather_date
        > (select max(weather_date) from {{ this }}) - interval {{ var('lookback_days', 2) }} day
{% endif %}
