-- Сингулярный тест: строки, которые он вернёт, — нарушения
select city_id, days, rainy_days from {{ ref('mart_city_rainy_days') }} where rainy_days > days
