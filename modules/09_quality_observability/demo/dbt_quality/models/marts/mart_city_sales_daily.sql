select city_id, sales_date, round(sum(sales), 3) as sales, count(*) as stores
from {{ ref('stg_store_sales') }}
group by city_id, sales_date
