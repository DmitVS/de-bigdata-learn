---
type: term
aliases: [Airflow, DAG Airflow, TaskFlow, XCom, оператор, operator, Airflow Asset, Execution API]
tags: [orchestration]
---

# Apache Airflow

**Task-ориентированный оркестратор: DAG — Python-файл с задачами (операторы или `@task` в стиле TaskFlow), значения между задачами — XCom. В Airflow 3 задачи отчитываются api-серверу по HTTP (Execution API), а `Asset` — метка данных, по событиям которой можно запускать другие DAG.** Стандарт индустрии с огромной экосистемой.

> [!tip] Аналогия
> Диспетчерская, которая мыслит рейсами и действиями, а не грузом на станциях.

**У нас:** профиль `airflow` (`airflow standalone`, SQLite, порт 8081), DAG `weather_daily` и `rainy_report` в `modules/06_orchestration/airflow_demo/dags/`. Ловушки слоя: адрес Execution API с хостовым портом → `Connection refused`; UID 50000 → `PermissionError` на томе.

Связано: [оркестратор](orchestrator.md) · [логическая дата](logical-date.md)
