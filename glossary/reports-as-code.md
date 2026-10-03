---
type: term
aliases: [Отчёт как код, reports as code, Evidence, источник Evidence, срез]
tags: [bi, docs]
---

# Отчёт как код (Evidence)

**Отчёт — файл markdown в git: текст, SQL и графики вместе; сборка — статический сайт.** В
Evidence запросы `sources/` выполняются в базе и сохраняются в Parquet, SQL страницы выполняет
DuckDB WASM в браузере. Изменения отчёта ревьюят как код. Всё, что выгружено в срез, лежит в
сайте.

> [!tip] Аналогия
> Статья с выводом, напечатанная выпуском: читать можно без автора и без архива.

**У нас:** открытый фреймворк `@evidence-dev/evidence` 40.1.8 + коннектор Trino, учебный отчёт
`modules/10_serving_bi/demo/evidence_report`, http://localhost:3071, сборка — `make report`
(87 МБ, данные — 41 КБ). DATE из Trino — строкой, иначе `Cannot convert … to a BigInt`.

Связано: [docs as code](docs-as-code.md) · [Superset](superset.md) · [Trino](trino.md)
