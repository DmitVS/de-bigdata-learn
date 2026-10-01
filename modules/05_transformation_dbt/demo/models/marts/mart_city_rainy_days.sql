select
    city_id,
    count(*) as days,
    count(*) filter (where precipitation >= {{ var('rainy_threshold', 10.0) }}) as rainy_days,
    round(avg(avg_temperature), 2) as avg_temperature
from {{ ref('int_city_weather_daily') }}
group by city_id
