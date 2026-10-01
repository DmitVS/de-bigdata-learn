select
    city_id,
    weather_date,
    avg(precipitation) as precipitation,
    avg(avg_temperature) as avg_temperature,
    count(*) as stores
from {{ ref('stg_weather') }}
group by city_id, weather_date
