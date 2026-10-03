---
type: term
aliases: [OpenLineage, RunEvent, facet, фасет, symlinks, columnLineage, агент OpenLineage]
tags: [governance, lineage]
---

# OpenLineage

**Открытый стандарт событий lineage.** Задача при запуске отправляет `RunEvent`: тип (`START`,
`RUNNING`, `COMPLETE`, `FAIL`), запуск (`runId`), задачу (`namespace` + `name`), входные и
выходные датасеты. Подробности — в **фасетах** (facets): схема, `symlinks` (имя таблицы в
каталоге), `columnLineage` (колонка ← колонки + тип преобразования), статистика вывода. Доставка —
транспортом: console, file, http, kafka, composite.

> [!tip] Аналогия
> Протокол очевидца: кто, когда, что взял и что получил — в одной форме для всех.

**У нас:** агент `openlineage-spark` 1.53.0 в образе Spark (`make spark-lineage`): выход назван
по S3 (`s3://warehouse`, `lakehouse/<uuid>`), имя таблицы — в `symlinks`
(`governance_demo.store_sales_daily`), `rowCount` 87 106. Python — `openlineage-python`
(`demo/emit_lineage.py`). Приём в OpenMetadata — `POST /api/v1/openlineage/lineage`.

Связано: [lineage](lineage.md) · [каталог данных](data-catalog.md) · [Spark](spark.md)
