# Модуль 10 · Витрины и BI

**Длительность:** ~1–2 нед. · **Статус и DoD:** см. [ROADMAP](../../ROADMAP.md)

## Бизнес-вопрос

> Как отдать данные бизнесу быстро и так, чтобы все считали метрики одинаково?

## Цели

- выбрать движок для витрин
- построить дашборд сети
- определить метрики в одном месте

## Темы

- ClickHouse: MergeTree как LSM-дерево, ORDER BY, materialized views
- стоимость запроса: сколько строк и байт прочитано
- Trino: федеративные запросы, коннекторы Iceberg/Postgres/ClickHouse
- BI: Superset — датасеты, чарты, дашборды; основы визуализации
- семантический слой и метрики

## Инструменты

ClickHouse, Trino, Superset (слой `serving.yaml`)

## Лабы

Каждая лаба — папка `labs/<номер>_<название>/` с README по [шаблону](../../templates/lab_README.md).

- [ ] 10.1 — ClickHouse: витрины из marts
- [ ] 10.2 — Trino: один запрос через Iceberg + Postgres
- [ ] 10.3 — Superset: дашборд сети (минимум: распределение по категориям + динамика во времени)

## Мини-проект (вклад в capstone)

Дашборд: продажи, out-of-stock, промо, погода — со скриншотами в capstone.

## Ресурсы

- [Data-Learn: модуль 3 — BI](https://github.com/Data-Learn/data-engineering/blob/master/DE-101%20Modules/Module03/readme.md)
- [Surfalytics: Trino](https://github.com/surfalytics/data-projects/tree/main/de-projects/05_trinodb)
- [Surfalytics: Open-source BI with Metabase](https://github.com/surfalytics/data-projects/tree/main/async-projects/03-Open-Source-BI-with-Metabase)

## Книга и видео

Полная таблица с пояснениями, зачем читать и что пропустить — в [карте чтения](../../reading_map.md#10--витрины-и-bi).

- 📖 Клеппман, гл. 3 — LSM-деревья (основа MergeTree)
- 🎬 [Zoomcamp `03-data-warehouse`](https://github.com/DataTalksClub/data-engineering-zoomcamp/tree/main/03-data-warehouse) — best practices и стоимость запроса

## Домашка-чекпоинт

После всех лаб — `homework.md` по [шаблону](../../templates/homework.md).

## Заметки

Конспект, тезисы по книге и выводы — в [`notes.md`](notes.md).
