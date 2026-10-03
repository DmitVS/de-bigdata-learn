---
type: term
aliases: [Superset, датасет, dataset, чарт, chart, дашборд, dashboard, native filter, cross-filter]
tags: [bi]
---

# Apache Superset

**BI-инструмент с открытым кодом.** Метаданные (подключения, датасеты, чарты, дашборды)
хранит в своей базе, данные каждый раз запрашивает у подключённых СУБД через SQLAlchemy и
кэширует ответ. **Датасет** — таблица или SQL с метриками и подписями; **чарт** — график по
датасету; **дашборд** — чарты и фильтры.

> [!tip] Аналогия
> Витрина магазина: полка с ценниками (датасет), товар на витрине (чарт), вся витрина (дашборд).

**У нас:** `debd/superset:6.1.0` (+ clickhouse-connect, trino, psycopg2), http://localhost:8088,
метаданные — база `superset` в Postgres, кэш 600 с. Метрика `SUM(oos_hours) / (16 * COUNT(*))`
даёт 19,75 % по сети — как MetricFlow.

Связано: [семантический слой](semantic-layer.md) · [метрика](metric.md) · [слой отдачи](serving-layer.md)
