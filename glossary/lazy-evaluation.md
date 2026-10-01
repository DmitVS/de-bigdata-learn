---
type: term
aliases: [lazy, eager, ленивое выполнение, LazyFrame, scan_parquet, projection pushdown, predicate pushdown]
tags: [движки, производительность]
---

# Жадное и ленивое выполнение

**Жадный движок выполняет каждую команду сразу; ленивый сначала строит план всего запроса, оптимизирует (отсекает колонки, проталкивает фильтры в чтение) и только потом выполняет.** DuckDB SQL и Polars `scan_parquet` — ленивые; pandas и Polars `read_parquet` — жадные.

> [!tip] Аналогия
> Сначала прочитать весь заказ и взять с полок только нужное — или вынести на пол всё и потом перебирать.

**У нас:** агрегат по `train.parquet`: DuckDB 0,49 с / 0,6 ГБ, Polars lazy 0,47 с / 2,8 ГБ, pandas (4 колонки) 5,8 с / 3,9 ГБ. План Polars: `PROJECT 3/19 COLUMNS`.

Связано: [план запроса](query-plan.md) · [отсечение](pruning.md) · [колоночное хранение](columnar-storage.md)
