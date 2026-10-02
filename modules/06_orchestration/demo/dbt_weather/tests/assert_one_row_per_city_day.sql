-- Grain stg_weather — город × день. Дубль означает, что загрузка дня прошла дважды без merge.
select city_id, weather_date, count(*) as n
from {{ ref('stg_weather') }}
group by city_id, weather_date
having count(*) > 1
