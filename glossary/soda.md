---
type: term
aliases: [Soda, Soda Core, soda contract verify, data source Soda, failed_rows, metric check]
tags: [quality]
---

# Soda Core

**Инструмент проверки данных: источник данных (YAML с подключением) и контракт на набор данных (колонки и проверки: missing, invalid, schema, duplicate, freshness, row_count, metric, failed_rows) с порогами и уровнями fail / warn. `soda contract verify` возвращает код: 0 — прошло, 1 — провал, 2 — только предупреждения, 3 — ошибка выполнения.**

> [!tip] Аналогия
> Контролёр на приёмке с бланком.

**У нас:** Soda Core 4.25 + soda-duckdb (группа `quality`); `modules/09_quality_observability/demo/soda/`. Раздел `columns` обязателен; генератор источников знает только Postgres. Python API принимает готовое соединение DuckDB (`from_existing_cursor`, можно с `ATTACH` Iceberg) и `data_timestamp` для свежести на исторических данных.

Связано: [контракт данных](data-contract.md) · [измерения качества](data-quality-dimensions.md) · [код выхода](exit-code.md)
