-- Погода повторяется в каждой строке магазин × товар: оставляем одну строку на магазин и день
with
    source as (
        select *
        from {{ source('raw', 'train') }}
        union all
        select *
        from {{ source('raw', 'eval') }}
    )

select distinct
    store_id,
    city_id,
    dt::date as weather_date,
    precpt as precipitation,
    avg_temperature,
    avg_humidity,
    avg_wind_level
from source
