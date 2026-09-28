# Модуль 13 · (Опционально) Облачное хранилище: Snowflake

**Длительность:** ~1 нед. · **Статус и DoD:** см. [ROADMAP](../../ROADMAP.md)

## Бизнес-вопрос

> Чем облачный DWH отличается от своего lakehouse по цене, удобству и возможностям?

## Цели

- перенести dbt-проект в Snowflake
- сравнить подходы

## Темы

- архитектура Snowflake: storage/compute, warehouses, credits
- Snowflake + Iceberg
- стоимость владения: облако vs self-hosted

## Инструменты

Snowflake trial (единственный модуль вне локального Docker)

## Лабы

Каждая лаба — папка `labs/<номер>_<название>/` с README по [шаблону](../../templates/lab_README.md).

- [ ] 13.1 — загрузка данных в Snowflake
- [ ] 13.2 — dbt-проект на Snowflake
- [ ] 13.3 — сравнение

## Мини-проект (вклад в capstone)

Эссе: когда выбирать облачный DWH, а когда lakehouse.

## Ресурсы

- [Data-Learn: модуль 6 — аналитические хранилища](https://github.com/Data-Learn/data-engineering/blob/master/DE-101%20Modules/Module06/readme.md)
- [Surfalytics: Snowflake and Iceberg lakehouse](https://github.com/surfalytics/data-projects/tree/main/de-projects/16_snowflake_and_iceberg_lakehouse)

## Книга и видео

Полная таблица с пояснениями, зачем читать и что пропустить — в [карте чтения](../../reading_map.md#13--опц-облачное-хранилище).

- 🎬 [Zoomcamp `03-data-warehouse`](https://github.com/DataTalksClub/data-engineering-zoomcamp/tree/main/03-data-warehouse) — BigQuery для сравнения со Snowflake

## Домашка-чекпоинт

После всех лаб — `homework.md` по [шаблону](../../templates/homework.md).

## Заметки

Конспект, тезисы по книге и выводы — в [`notes.md`](notes.md).
