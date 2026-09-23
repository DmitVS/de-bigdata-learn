# Модуль 04 · Ingestion (EL)

**Длительность:** ~1 нед. · **Статус и DoD:** см. [ROADMAP](../../ROADMAP.md)

## Бизнес-вопрос

> Как надёжно и инкрементально забирать данные из файлов, учётной системы и внешних API?

## Цели

- строить идемпотентную инкрементальную загрузку
- понимать паттерны ingestion
- подготовить OLTP-источник для CDC

## Темы

- паттерны: full load, incremental (watermark / cursor), CDC, append vs merge
- идемпотентность, повторные запуски, backfill
- schema contracts и эволюция схем источника
- загрузка из API: пагинация, rate limits, ретраи
- Polars vs pandas vs SQL для трансформаций на лету

## Инструменты

dlt, Postgres (retail_oltp), Polars, DuckDB

## Лабы

Каждая лаба — папка `labs/<номер>_<название>/` с README по [шаблону](../../templates/lab_README.md).

- [ ] 04.1 — dlt: файлы из S3 `landing` → Iceberg, инкрементально
- [ ] 04.2 — справочники сети в Postgres `retail_oltp` + генератор изменений (цены, промо, новые магазины)
- [ ] 04.3 — dlt: Postgres → lakehouse, full vs incremental
- [ ] 04.4 — dlt: публичный API (например, погода/праздники) → lakehouse
- [ ] 04.5 — одна трансформация: SQL / Polars / pandas

## Мини-проект (вклад в capstone)

Три источника (файлы, OLTP, API) загружаются в bronze одной командой.

## Ресурсы

- [Surfalytics: data ingestion patterns](https://github.com/surfalytics/data-projects/tree/main/async-projects/06-data-ingestion-patterns)
- [Surfalytics: db to db with Python](https://github.com/surfalytics/data-projects/tree/main/de-projects/08_db_to_db_python)
- [dlt docs](https://dlthub.com/docs/intro)
- [Polars user guide](https://docs.pola.rs/user-guide/)

## Заметки

Конспект и выводы — в [`notes.md`](notes.md).
