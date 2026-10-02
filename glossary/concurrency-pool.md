---
type: term
aliases: [пул конкурентности, pool, concurrency, max_concurrent_runs, Could not set lock]
tags: [orchestration]
---

# Пул конкурентности

**Именованный лимит на число шагов, которые одновременно используют общий ресурс во всех запусках. Шаг с занятым слотом ждёт (`Step blocked by limit for pool …`). Отдельно ограничивают число одновременных запусков.**

> [!tip] Аналогия
> Одноколейный участок: поезда проходят его по одному.

**У нас:** `pool="duckdb"` у всех шагов, открывающих `demo_orchestration.duckdb`, лимит 1 в `concurrency.pools` (`dagster.yaml`); `concurrency.runs.max_concurrent_runs: 4`. Без пула у читающей проверки backfill падал с `Could not set lock on file`.

**Посмотреть:** `make dagster ARGS="instance concurrency get --all"`.

Связано: [гонка](race-condition.md) · [оркестратор](orchestrator.md)
