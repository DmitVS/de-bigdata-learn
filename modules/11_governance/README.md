# Модуль 11 · Governance: каталог, lineage, доступы

**Длительность:** ~1 нед. · **Статус и DoD:** см. [ROADMAP](../../ROADMAP.md)

## Бизнес-вопрос

> Кто владеет данными, откуда они пришли и кому их можно видеть?

## Цели

- развернуть каталог данных
- собрать lineage
- настроить доступы

## Темы

- каталог и glossary, владельцы данных
- теория lineage: по таблицам и по колонкам, статический (из кода) и рантайм (из запусков); анализ влияния и поиск причины
- стандарт OpenLineage: события запусков из Spark, dbt, Dagster в одном формате
- column-level lineage из dbt/Dagster
- RBAC, маскирование, PII
- этика данных и ответственность инженера (Клеппман, гл. 12)

## Инструменты

OpenMetadata (слой `governance.yaml`, запускать отдельно — ~6 ГБ RAM)

## Лабы

Каждая лаба — папка `labs/<номер>_<название>/` с README по [шаблону](../../templates/lab_README.md).

- [ ] 11.1 — OpenMetadata: подключить Iceberg, Postgres, dbt
- [ ] 11.2 — lineage и glossary; приём lineage из Spark через OpenLineage — граф от источника через Spark и dbt до дашборда
- [ ] 11.3 — роли и маскирование в Trino/Postgres

## Мини-проект (вклад в capstone)

Каталог с lineage от источника до дашборда.

## Ресурсы

- [OpenMetadata docs](https://docs.open-metadata.org/)
- [OpenLineage: стандарт событий lineage](https://openlineage.io/docs/)
- [OpenLineage: интеграция со Spark](https://openlineage.io/docs/integrations/spark/)

## Книга и видео

Полная таблица с пояснениями, зачем читать и что пропустить — в [карте чтения](../../reading_map.md#11--governance).

- 📖 Клеппман, гл. 12 — последний раздел, этика данных

## Домашка-чекпоинт

После всех лаб — `homework.md` по [шаблону](../../templates/homework.md).

## Заметки

Конспект, тезисы по книге и выводы — в [`notes.md`](notes.md).
