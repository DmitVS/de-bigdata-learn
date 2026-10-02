---
type: term
aliases: [Spark, Apache Spark, driver, executor, worker, cluster manager, менеджер кластера]
tags: [batch]
---

# Apache Spark

**Движок распределённой обработки: driver строит и оптимизирует план, делит его на задачи и раздаёт executors — процессам JVM на workers; менеджер кластера выдаёт приложению ядра и память.** Параллелизм = ядра executors приложения. Окупается, когда данные или промежуточные результаты не помещаются на одну машину.

> [!tip] Аналогия
> Бригада: прораб (driver), рабочие (executors) на площадках (workers), отдел кадров (менеджер кластера).

**У нас:** слой `spark.yaml`: `spark-master` (UI 8090), 2 workers по 2 ядра, `spark-connect` — driver (UI 4040); образ `debd/spark:4.1.3` с Iceberg 1.12 и Python 3.12. Кластер в покое ~5,5 ГБ. На нашем датасете DuckDB быстрее — Spark в курсе ради модели и атомарной записи в Iceberg.

Связано: [Spark Connect](spark-connect.md) · [job, stage, task](spark-job-stage-task.md) · [shuffle](shuffle.md)
