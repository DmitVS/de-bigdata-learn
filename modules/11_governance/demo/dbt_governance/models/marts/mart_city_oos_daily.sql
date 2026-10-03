select
    s.city_id,
    s.dt,
    sum(s.sales) as sales,
    sum(s.oos_hours) as oos_hours,
    sum(s.shelf_hours) as shelf_hours,
    count_if(st.is_open) as open_stores
from {{ ref("stg_store_sales_daily") }} as s
join {{ ref("stg_stores") }} as st on st.store_id = s.store_id
group by s.city_id, s.dt
