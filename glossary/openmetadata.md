---
type: term
aliases: [OpenMetadata, OM, metadata ingest, om-ingest, сбор метаданных, ingestion-bot]
tags: [governance]
---

# OpenMetadata

**Каталог данных с открытым кодом: сервер API и UI, хранилище сущностей (Postgres или MySQL) и
поисковый индекс (Elasticsearch/OpenSearch).** Метаданные приходят сбором (`metadata ingest` по
YAML: коннекторы Trino, Postgres, dbt, Superset и сотни других), событиями OpenLineage и правками
людей. Сущности — сервис → база → схема → таблица → колонка; у каждой FQN, владельцы, теги,
термины глоссария, lineage.

> [!tip] Аналогия
> Библиотечная картотека с роботом, который сам обходит полки, и библиотекарями, которые пишут
> аннотации.

**У нас:** 2.0.3 на нашем Postgres 17 + Elasticsearch 9.3, UI http://localhost:8585; сбор —
`make om-ingest CFG=…` (CLI в образе `openmetadata/ingestion`, переменные `${…}` из окружения);
`make om-token` — токен бота. Найдено на стеке: сервис `openlineage` и пайплайны для событий
OpenLineage нужно создать заранее (2.0.3 падает на `updatedat`); владельцы из dbt назначаются,
только если команда уже есть.

Связано: [каталог данных](data-catalog.md) · [OpenLineage](openlineage.md) · [lineage](lineage.md)
