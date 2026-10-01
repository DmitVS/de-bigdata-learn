---
type: term
aliases: [SQLMesh, виртуальное окружение, plan, Breaking, Non-breaking, table_diff]
tags: [transform, инструмент]
---

# SQLMesh

**Фреймворк трансформаций, который разбирает SQL сам (sqlglot): зависимости без `ref`, классификация изменений Breaking / Non-breaking, учёт построенных интервалов, блокирующие аудиты.** Каждая версия модели — физическая таблица, окружения (prod, dev) — представления над ними; выкатка в prod — переключение представлений без пересчёта.

> [!tip] Аналогия
> Тестовый зал кухни: блюдо готовят и пробуют там, а на раздаче просто меняют табличку.

**У нас:** SQLMesh 0.228 (группа `transform`), демо `modules/05_transformation_dbt/demo_sqlmesh/`: добавление колонки — Non-breaking, фильтр — Breaking; выкатка из dev — «No physical layer updates».

Связано: [dbt](dbt-core.md) · [lineage](lineage.md)
