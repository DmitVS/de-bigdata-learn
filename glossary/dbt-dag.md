---
type: term
aliases: [DAG, граф моделей, manifest.json, селектор, state:modified]
tags: [transform]
---

# Граф dbt и селекторы

**Ориентированный граф без циклов, который dbt строит из вызовов `ref()` и `source()`; хранится в `target/manifest.json` (`nodes`, `parent_map`, `child_map`).** Селекторы выбирают часть графа: `m+` — потомки, `+m` — предки, `@m`, `tag:`, `path:`, `state:modified+`.

> [!tip] Аналогия
> Порядок готовки, выведенный из того, какие заготовки нужны каждому рецепту.

**У нас:** `dbt ls -s stg_weather+` — анализ влияния; `state:modified+ --state <папка>` — основа slim CI (модуль 12).

Связано: [dbt](dbt-core.md) · [lineage](lineage.md)
