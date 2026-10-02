select city_id from {{ ref('mart_city_rainy_days') }} where rainy_days > days
