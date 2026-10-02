---
type: term
aliases: [оркестратор, orchestration, оркестрация, run, запуск, daemon, webserver]
tags: [orchestration]
---

# Оркестратор

**Система, которая запускает шаги pipeline в порядке зависимостей, по расписанию или событию, повторяет упавшие шаги и хранит историю запусков.** Сам данные не обрабатывает: решает, когда и в каком порядке запустить dlt, dbt, Spark.

> [!tip] Аналогия
> Диспетчерская железной дороги: сама грузы не возит, но знает маршруты, расписание и что делать при сбое на линии.

**У нас:** Dagster (слой `orchestration.yaml`: webserver — UI на 3070, daemon — расписания и очередь, code-сервер `dagster-demo` — код и запуски, история — база `dagster` в Postgres); Airflow 3 для сравнения (профиль `airflow`, порт 8081).

**Посмотреть:** `make ps | grep dagster`, <http://localhost:3070>.

Связано: [ассет](software-defined-asset.md) · [code location](code-location.md) · [расписание и сенсор](schedule-sensor.md) · [Airflow](airflow.md)
