---
type: term
aliases: [AQE, Adaptive Query Execution, адаптивное выполнение, isFinalPlan]
tags: [batch]
---

# AQE (Adaptive Query Execution)

**Пересмотр плана Spark во время выполнения по реальным размерам после каждой стадии shuffle: объединение мелких партиций до `advisoryPartitionSizeInBytes` (64 МБ), замена sort-merge на broadcast join, разрезание перекошенных партиций (выше 256 МБ и в 5 раз больше медианы).** Итоговый план — в UI → SQL (`isFinalPlan=true`); `explain()` показывает план до запуска.

> [!tip] Аналогия
> Прораб перекраивает план по фактическим объёмам.

**У нас:** без AQE после groupBy 200 задач, с AQE — 1; партицию города 0 (~100 МБ) AQE не разделил — перекос лечили broadcast и солью.

Связано: [shuffle](shuffle.md) · [соединения в Spark](spark-joins.md) · [перекос](data-skew.md)
