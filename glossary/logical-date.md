---
type: term
aliases: [логическая дата, logical date, ds, data interval, интервал данных, catchup]
tags: [orchestration]
---

# Логическая дата и интервал данных

**В Airflow у каждого DAG run есть интервал данных `[start, end)`; логическая дата — его начало. Run за интервал запускается после его конца: daily-run за 1 апреля стартует 2 апреля в 00:00. `catchup=True` при включении DAG создаёт runs за все прошедшие интервалы.** Аналог ключа партиции, но статус хранится у run, а не у данных.

> [!tip] Аналогия
> Дата в расписании, за которую ходит рейс, а не время отправления.

**У нас:** `airflow dags test weather_daily 2024-04-01`, `airflow dags trigger weather_daily -l 2024-04-03T00:00:00+00:00`; в задаче — параметр `ds`.

Связано: [Airflow](airflow.md) · [партиции ассета](asset-partitions.md) · [backfill](backfill.md)
