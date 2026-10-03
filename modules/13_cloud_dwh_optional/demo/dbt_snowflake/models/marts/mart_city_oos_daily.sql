select
    city_id,
    dt,
    sum(sale_amount) as sales,
    sum(oos_hours) as oos_hours,
    16 * count(*) as shelf_hours,
    sum(iff(is_promo, sale_amount, 0)) as promo_sales
from {{ ref("stg_sales") }}
group by city_id, dt
