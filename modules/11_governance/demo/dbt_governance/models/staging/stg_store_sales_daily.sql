select store_id, city_id, dt, sales, oos_hours, 16 * products as shelf_hours
from {{ source("spark", "store_sales_daily") }}
