---
type: term
aliases: [ассет, asset, software-defined asset, материализация, materialization, asset key, ключ ассета]
tags: [orchestration]
---

# Ассет (software-defined asset)

**Описание объекта данных в коде: ключ (имя), функция, которая его получает, и входы. Материализация — успешный запуск функции, после которого Dagster записывает событие с временем, партицией и метаданными.** Оркестратор знает состояние данных, а не только «процесс завершился».

> [!tip] Аналогия
> Станция на карте: что на ней должно появиться и откуда везут груз.

**У нас:** `@asset` в `modules/06_orchestration/demo/weather_orchestration/assets/`; `@dlt_assets` и `@dbt_assets` создают по ассету на таблицу dlt и модель dbt. Ключ ≠ имя таблицы: где лежат данные, решает функция.

**Посмотреть:** `make dagster ARGS="asset list"`, UI → Assets → View lineage.

Связано: [оркестратор](orchestrator.md) · [проверка ассета](asset-check.md) · [lineage](lineage.md)
