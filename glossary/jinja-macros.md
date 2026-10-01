---
type: term
aliases: [Jinja, макрос, macro, run-operation, dbt_utils, packages.yml, dbt deps]
tags: [transform]
---

# Jinja, макросы и пакеты dbt

**Jinja — язык шаблонов: `{{ }}` вставляет значение, `{% %}` — логика (set, for, if); выполняется до отправки SQL в базу. Макрос — функция Jinja, возвращающая текст SQL. Пакет — чужой dbt-проект с макросами (`packages.yml` → `dbt deps`).**

> [!tip] Аналогия
> Кулинарный приём, вызываемый по имени, и книга приёмов других кухонь.

**У нас:** демо: `precipitation_bucket()` (CASE), операция `print_row_counts`; dbt_utils 1.4.1: `generate_surrogate_key`, `date_spine` (конец не включён, TIMESTAMP).

Связано: [dbt](dbt-core.md) · [суррогатный ключ](surrogate-key.md)
