---
type: term
aliases: [ресурс, resource, ConfigurableResource, EnvVar, Config, конфиг запуска]
tags: [orchestration]
---

# Ресурс Dagster

**Объект подключения к внешней системе (S3, DuckDB, dbt, dlt), который Dagster передаёт в ассет параметром по имени. Поля ресурса берутся из окружения через `EnvVar`; параметры конкретного запуска — отдельно, через `Config`.** Ресурс отделяет «что делает шаг» от «куда он подключается».

> [!tip] Аналогия
> Телефонная линия депо: станция звонит по ней, не зная номера наизусть.

**У нас:** `S3Resource` и `DuckDBResource` в `demo/weather_orchestration/resources.py`; ключи в `Definitions(resources={"s3": …, "duck": …})` совпадают с именами параметров ассетов. `EnvVar` вне Dagster не разрешается → `Invalid endpoint` у s3fs.

Связано: [ассет](software-defined-asset.md) · [переменная окружения](environment-variable.md)
