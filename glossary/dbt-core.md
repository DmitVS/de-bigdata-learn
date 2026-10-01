---
type: term
aliases: [dbt, dbt-core, модель dbt, profiles.yml, dbt_project.yml, source, ref]
tags: [transform, инструмент]
---

# dbt (data build tool)

**Компилятор и планировщик SQL-трансформаций: модель — один SELECT в файле, зависимости — через `ref()` и `source()`, а dbt сам оборачивает SELECT в DDL, строит граф и выполняет модели по порядку.** Считает не dbt, а база через адаптер. Рядом с кодом — тесты, описания, snapshots.

> [!tip] Аналогия
> Кухня, где повар пишет только рецепты, а порядок готовки и посуду выбирает кухня.

**У нас:** dbt-core 1.12 + dbt-duckdb 1.11; модели строятся в файле DuckDB, bronze читается из Iceberg через `attach`, витрины публикуются в Iceberg post-hook'ом. Демо — `modules/05_transformation_dbt/demo/`, capstone — `capstone/transform/`.

Связано: [граф dbt](dbt-dag.md) · [материализация](materialization.md) · [медальон](medallion.md)
