---
type: term
aliases: [партиция Spark, partition, repartition, coalesce, maxPartitionBytes]
tags: [batch]
---

# Партиция в Spark

**Кусок данных DataFrame, который обрабатывает одна задача. При чтении файлов число партиций зависит от размера данных, `spark.sql.files.maxPartitionBytes` и числа ядер; после shuffle — от `spark.sql.shuffle.partitions` (200) и AQE.** `repartition` меняет число с shuffle, `coalesce` уменьшает без него.

> [!tip] Аналогия
> Участок работы одного рабочего.

**У нас:** `train.parquet` (106 МБ) читается 4 задачами — по одной на ядро. Не путать с партициями таблицы Iceberg (хранение) и партициями ассета Dagster (перезапуск).

Связано: [shuffle](shuffle.md) · [партиционирование таблиц](partitioning.md) · [AQE](aqe.md)
