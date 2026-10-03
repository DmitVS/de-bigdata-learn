-- Колонки Parquet в Snowflake — в нижнем регистре и в кавычках (как в файле); здесь их
-- переименовываем в обычные идентификаторы.
select
    "store_id" as store_id,
    "city_id" as city_id,
    "product_id" as product_id,
    to_date("dt") as dt,
    "sale_amount" as sale_amount,
    "stock_hour6_22_cnt" as oos_hours,
    "activity_flag" = 1 as is_promo
from {{ source("raw", "sales") }}
