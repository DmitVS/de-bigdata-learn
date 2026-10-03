---
title: Где и когда полки пустеют
---

Отчёт модуля 10 (урок 07). Данные — витрины `serving_demo` в Iceberg через Trino. Доля часов без
товара — часы без товара на полке с 6 до 22, делённые на все часы работы полки, из сумм.

```sql cities
select distinct cast(city_id as integer) as city_id from lake.city_day order by city_id
```

<Dropdown name=city data={cities} value=city_id title="Город">
    <DropdownOption value=-1 valueLabel="Вся сеть"/>
</Dropdown>

```sql totals
select
    sum(oos_hours) / sum(shelf_hours)  as oos_share,
    sum(promo_sales) / sum(sales)      as promo_share,
    sum(sales)                         as sales
from lake.city_day
where ${inputs.city.value} = -1 or city_id = ${inputs.city.value}
```

## Вывод

Полка пустует <Value data={totals} column=oos_share fmt=pct1/> рабочих часов. Продажи в промо — <Value data={totals} column=promo_share fmt=pct1/> всех продаж.

```sql by_city
select
    'город ' || cast(city_id as integer) as city,
    sum(oos_hours) / sum(shelf_hours)   as oos_share
from lake.city_day
group by city_id
order by oos_share desc
```

## Какие города пустеют чаще

<BarChart data={by_city} x=city y=oos_share yFmt=pct1 swapXY=true sort=false
    title="Доля часов без товара по городам"/>

```sql by_day
select
    dt::date as dt,
    sum(oos_hours) / sum(shelf_hours) as oos_share,
    sum(sales)                        as sales
from lake.city_day
where ${inputs.city.value} = -1 or city_id = ${inputs.city.value}
group by 1
order by 1
```

## Как меняется во времени

<LineChart data={by_day} x=dt y=oos_share yFmt=pct1 title="Доля часов без товара по дням"/>

Март и июль в датасете неполные: 4 и 2 дня. Поэтому график — по дням, а не по месяцам.

```sql by_category
select
    first_category_id,
    sum(oos_hours) / sum(shelf_hours) as oos_share,
    sum(sales)                        as sales
from lake.category_city
where ${inputs.city.value} = -1 or city_id = ${inputs.city.value}
group by first_category_id
order by oos_share desc
```

## Какие категории

<DataTable data={by_category}>
    <Column id=first_category_id fmt=id title="Категория"/>
    <Column id=oos_share fmt=pct1 title="Доля без товара"/>
    <Column id=sales fmt=num0 title="Продажи"/>
</DataTable>

## Как считали

- Источник: `sources/lake/*.sql` — Trino агрегирует витрины до города × дня и категории × города.
- Запросы страницы выполняет DuckDB в браузере над выгруженными срезами.
- Доля — из сумм: среднее долей по городам дало бы другое число (урок 06).
