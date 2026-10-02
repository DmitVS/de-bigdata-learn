-- Дождливый день — средние осадки по магазинам города больше 1.
select
    city_id,
    count(*) filter (where precipitation > 1) as rainy_days,
    count(*) as days,
    round(avg(avg_temperature), 1) as avg_temperature
from {{ ref('stg_weather') }}
group by city_id
