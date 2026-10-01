---
type: term
aliases: [data test, unit test, generic test, singular test, store_failures, severity, аудит]
tags: [transform, качество]
---

# Тесты dbt: данные и логика

**Тест данных — SELECT, возвращающий нарушения (0 строк — PASS); бывает generic (`unique`, `not_null`, `accepted_values`, `relationships`, свои) и сингулярный (файл в `tests/`). Unit-тест подставляет фикстуры вместо входов модели и сравнивает результат с ожиданием — проверяет логику, а не данные.**

> [!tip] Аналогия
> Дегустация готового блюда и проверка рецепта на контрольных продуктах.

**У нас:** демо: unit-тест ловит замену `>=` на `>` (rainy_days 2→1); `store_failures` пишет нарушения в `main_dbt_test__audit`; ephemeral-вход в unit-тесте не подменяется.

Связано: [dbt](dbt-core.md) · [сверка](reconciliation.md)
