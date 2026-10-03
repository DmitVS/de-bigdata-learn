---
type: term
aliases: [MV ClickHouse, materialized view, refreshable materialized view, -State, -Merge, uniqState, uniqMerge]
tags: [clickhouse]
---

# Materialized view в ClickHouse

**Обычная MV ClickHouse — триггер на вставку:** при каждом `INSERT` в источник выполняет свой
запрос над новой пачкой и пишет результат в таблицу-приёмник. Историю до создания не видит;
пачки считает независимо, поэтому строки одного ключа сливаются только при слиянии частей.
Неаддитивные метрики хранят состояниями: вставка `uniqState`, чтение `uniqMerge`.
**Refreshable MV** (`REFRESH EVERY …`) пересчитывает весь запрос по расписанию.

> [!tip] Аналогия
> Кассир дописывает итог каждой поставки в журнал; журнал сводят позже.

**У нас:** MV на таблицу с магазином 20 → 0 строк; ещё два магазина города 17 → 194 строки,
`FINAL` → 97.

Связано: [MergeTree](mergetree.md) · [материализация](materialization.md)
