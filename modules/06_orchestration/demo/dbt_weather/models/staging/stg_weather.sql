select city_id, dt as weather_date, precipitation, avg_temperature, avg_humidity, stores
from {{ source('bronze', 'weather') }}
