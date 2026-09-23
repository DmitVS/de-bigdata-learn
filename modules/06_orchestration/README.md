# Модуль 06 · Оркестрация: Dagster (+ Airflow)

**Длительность:** ~1 нед. · **Статус и DoD:** см. [ROADMAP](../../ROADMAP.md)

## Бизнес-вопрос

> Как запускать весь pipeline по расписанию, видеть зависимости и безопасно перезапускать?

## Цели

- описать pipeline как software-defined assets
- настроить расписания, сенсоры, партиции
- понимать разницу asset- и task-ориентированной оркестрации

## Темы

- DAG, идемпотентность, ретраи, backfill, партиции по времени
- Dagster: assets, resources, schedules, sensors, интеграции dbt и dlt
- Airflow 3: DAG, operators, TaskFlow — для сравнения
- где хранить состояние и секреты

## Инструменты

Dagster (новый слой `orchestration.yaml`), Airflow (опц.)

## Лабы

Каждая лаба — папка `labs/<номер>_<название>/` с README по [шаблону](../../templates/lab_README.md).

- [ ] 06.1 — Dagster в compose, assets для dlt
- [ ] 06.2 — dbt-проект как assets
- [ ] 06.3 — партиции по дням и backfill
- [ ] 06.4 — (опц.) тот же pipeline на Airflow

## Мини-проект (вклад в capstone)

Pipeline 03–05 запускается по расписанию, падения видны в UI.

## Ресурсы

- [Dagster docs](https://docs.dagster.io/)
- [Surfalytics: Airflow intro](https://github.com/surfalytics/data-projects/tree/main/de-projects/22_airflow_intro)

## Заметки

Конспект и выводы — в [`notes.md`](notes.md).
