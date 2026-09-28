# Модуль 09 · Качество и наблюдаемость данных

**Длительность:** ~1 нед. · **Статус и DoD:** см. [ROADMAP](../../ROADMAP.md)

## Бизнес-вопрос

> Как узнать о проблеме в данных раньше, чем её заметит бизнес?

## Цели

- покрыть ключевые таблицы проверками
- настроить наблюдаемость dbt
- сформулировать SLO pipeline

## Темы

- измерения качества: полнота, уникальность, свежесть, валидность, согласованность
- dbt tests vs Soda vs Great Expectations
- data contracts
- observability: Elementary, аномалии объёма и свежести
- SLA/SLO/SLI через перцентили (p95 свежести), MTTD/MTTR, постмортемы
- reconciliation: сверка источника и витрины

## Инструменты

dbt tests, Soda Core, Elementary

## Лабы

Каждая лаба — папка `labs/<номер>_<название>/` с README по [шаблону](../../templates/lab_README.md).

- [ ] 09.1 — Soda checks на bronze/silver
- [ ] 09.2 — Elementary: отчёт и алерты
- [ ] 09.3 — SLO и разбор инцидента (намеренно сломать источник)

## Мини-проект (вклад в capstone)

`ops/slo.md` + первый постмортем в `ops/incidents.md`.

## Ресурсы

- [Surfalytics: Elementary + dbt](https://github.com/surfalytics/data-projects/tree/main/de-projects/09_elementary_dbt)
- [Surfalytics: Soda Core](https://github.com/surfalytics/data-projects/tree/main/de-projects/07_soda_core_snowflake)
- [Soda docs](https://docs.soda.io/)

## Книга и видео

Полная таблица с пояснениями, зачем читать и что пропустить — в [карте чтения](../../reading_map.md#09--качество-и-наблюдаемость).

- 📖 Клеппман, гл. 1 — перцентили (повтор)
- 📖 Клеппман, гл. 12 — проверка целостности (по желанию)
- 🎬 [Zoomcamp `05-data-platforms`](https://github.com/DataTalksClub/data-engineering-zoomcamp/tree/main/05-data-platforms) — часть про качество данных (по желанию)

## Домашка-чекпоинт

После всех лаб — `homework.md` по [шаблону](../../templates/homework.md).

## Заметки

Конспект, тезисы по книге и выводы — в [`notes.md`](notes.md).
