select store_id, city_id, dt as sales_date, sales, products, stock_hours, loaded_at
from {{ source('raw', 'store_sales_daily') }}
