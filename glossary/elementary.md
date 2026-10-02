---
type: term
aliases: [Elementary, edr, edr report, volume_anomalies, column_anomalies, dimension_anomalies, freshness_anomalies, anomaly_sensitivity, z-оценка]
tags: [quality]
---

# Elementary

**dbt-пакет и CLI наблюдаемости. Тесты-мониторы делят таблицу на корзины времени, сохраняют метрики (`data_monitoring_metrics`), по обучающему окну считают среднее и σ и помечают аномалией корзины окна обнаружения с |z| больше чувствительности (3). `edr report` собирает HTML-отчёт, `edr monitor` шлёт алерты.**

> [!tip] Аналогия
> Журнал завсклада с графиками и звонок директору.

**У нас:** пакет 0.26.0 + elementary-data 0.26 (группа `quality`), схема `main_elementary`; `--drop-day` → `The last row_count value is 376.000. The average for this metric is 880.600.`; отчёт — `data/elementary_report.html`.

Связано: [наблюдаемость данных](data-observability.md) · [тесты dbt](dbt-tests.md)
