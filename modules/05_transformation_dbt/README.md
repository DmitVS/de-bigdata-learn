# Модуль 05 · Трансформации: dbt (и SQLMesh)

**Длительность:** ~2 нед. · **Статус и DoD:** см. [ROADMAP](../../ROADMAP.md)

## Бизнес-вопрос

> Как превратить сырые данные в проверенные витрины, которым доверяет бизнес?

## Цели

- построить dbt-проект по слоям
- тестировать и документировать модели
- реализовать SCD2 и инкрементальность

## Темы

- слои staging / intermediate / marts, naming conventions
- materializations: view, table, incremental, ephemeral — trade-offs
- тесты: generic, singular, unit tests; документация и lineage
- snapshots (SCD2), макросы Jinja, пакеты (dbt_utils)
- SQLMesh: виртуальные окружения, plan/apply — сравнение с dbt

## Инструменты

dbt-core + dbt-duckdb (Iceberg через DuckDB), SQLMesh

## Лабы

Каждая лаба — папка `labs/<номер>_<название>/` с README по [шаблону](../../templates/lab_README.md).

- [ ] 05.1 — dbt init, sources, staging-модели
- [ ] 05.2 — звёздная схема из модуля 02 в marts
- [ ] 05.3 — тесты и docs
- [ ] 05.4 — incremental + snapshots по `retail_oltp`
- [ ] 05.5 — одна модель на SQLMesh

## Мини-проект (вклад в capstone)

Витрины «продажи», «out-of-stock», «эффект промо» в `capstone/transform`.

## Ресурсы

- [Data-Learn: модуль 4 — ETL/ELT и dbt](https://github.com/Data-Learn/data-engineering/blob/master/DE-101%20Modules/Module04/readme.md)
- [Surfalytics: dbt intro](https://github.com/surfalytics/data-projects/tree/main/de-projects/18_dbt_intro)
- [Surfalytics: SQLMesh intro](https://github.com/surfalytics/data-projects/tree/main/de-projects/19_sqlmesh_intro)
- [dbt best practices](https://docs.getdbt.com/best-practices)

## Книга и видео

Полная таблица с пояснениями, зачем читать и что пропустить — в [карте чтения](../../reading_map.md#05--трансформации-dbt).

- 📖 Клеппман, гл. 3 — материализованные представления (по желанию)
- 🎬 [Zoomcamp `04-analytics-engineering`](https://github.com/DataTalksClub/data-engineering-zoomcamp/tree/main/04-analytics-engineering) — модуль целиком: dbt + DuckDB

## Домашка-чекпоинт

После всех лаб — `homework.md` по [шаблону](../../templates/homework.md).

## Заметки

Конспект, тезисы по книге и выводы — в [`notes.md`](notes.md).
