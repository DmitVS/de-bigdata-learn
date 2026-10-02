---
type: term
aliases: [job, stage, task, задача Spark, стадия, Spark UI]
tags: [batch]
---

# Job, stage, task

**Действие (`count`, `collect`, `write`) запускает job; job делится на стадии по границам shuffle; стадия выполняется задачами — по одной на партицию входа.** В Spark UI: Jobs → Stages → Summary Metrics (медиана и максимум времени задач, shuffle, spill).

> [!tip] Аналогия
> Объект → этап → задание одному рабочему.

**У нас:** groupBy по магазинам: стадия чтения на 4 задачи → shuffle 38 КБ → 1 задача после AQE. `StageReport` в демо печатает стадии блока кода через REST API UI.

Связано: [ленивые вычисления](lazy-evaluation.md) · [shuffle](shuffle.md) · [Spark](spark.md)
