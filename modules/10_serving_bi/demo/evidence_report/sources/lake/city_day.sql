-- Срез для отчёта: город × день. Агрегат считает Trino, в отчёт попадает 18 × 97 строк,
-- а не 4,85 млн. Числитель и знаменатель доли хранятся отдельно (урок 06).
-- Дата — строкой: коннектор Trino в Evidence 40 падает на DATE и TIMESTAMP
-- («Cannot convert … to a BigInt»). Страница приводит её обратно: dt::date.
select
    s.city_id,
    cast(f.dt as varchar) as dt,
    sum(f.sale_amount) as sales,
    sum(f.oos_hours) as oos_hours,
    16 * count(*) as shelf_hours,
    sum(case when f.activity_flag = 1 then f.sale_amount else 0 end) as promo_sales,
    max(f.precpt) as precpt
from iceberg.serving_demo.fct_sales_daily as f
join iceberg.serving_demo.dim_store as s on s.store_id = f.store_id
group by s.city_id, cast(f.dt as varchar)
