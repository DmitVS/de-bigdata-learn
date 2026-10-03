-- Срез: категория первого уровня × город за весь период.
select
    p.first_category_id,
    s.city_id,
    sum(f.oos_hours) as oos_hours,
    16 * count(*) as shelf_hours,
    sum(f.sale_amount) as sales
from iceberg.serving_demo.fct_sales_daily as f
join iceberg.serving_demo.dim_store as s on s.store_id = f.store_id
join iceberg.serving_demo.dim_product as p on p.product_id = f.product_id
group by p.first_category_id, s.city_id
