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
- column-level lineage из dbt/Dagster
- RBAC, маскирование, PII

## Инструменты

OpenMetadata (слой `governance.yaml`, запускать отдельно — ~6 ГБ RAM)

## Лабы

Каждая лаба — папка `labs/<номер>_<название>/` с README по [шаблону](../../templates/lab_README.md).

- [ ] 11.1 — OpenMetadata: подключить Iceberg, Postgres, dbt
- [ ] 11.2 — lineage и glossary
- [ ] 11.3 — роли и маскирование в Trino/Postgres

## Мини-проект (вклад в capstone)

Каталог с lineage от источника до дашборда.

## Ресурсы

- [OpenMetadata docs](https://docs.open-metadata.org/)

## Заметки

Конспект и выводы — в [`notes.md`](notes.md).
