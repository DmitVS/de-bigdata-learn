---
type: term
aliases: [dbt docs, docs block, persist_docs, описание модели]
tags: [transform, документация]
---

# Документация как код

**Описания моделей и колонок хранятся в тех же YAML, что и код, проходят ревью вместе с ним и собираются в сайт (`dbt docs generate` → `manifest.json` + `catalog.json`) и в комментарии базы (`persist_docs`).** Docs-блок — именованный markdown для длинных и повторяющихся текстов.

> [!tip] Аналогия
> Технологическая карта рецепта лежит рядом с рецептом и не устаревает.

**У нас:** `dbt docs serve --host 0.0.0.0 --port 8580`; комментарии видны в `duckdb_tables().comment`; публикация в Iceberg их не переносит. CI-публикация сайта — модуль 12.

Связано: [lineage](lineage.md) · [граф dbt](dbt-dag.md)
