# Модуль 01 · Роль инженера данных и архитектура решения

**Длительность:** ~1 нед. · **Статус и DoD:** см. [ROADMAP](../../ROADMAP.md)

## Бизнес-вопрос

> Какие решения принимает сеть на основе данных и какая архитектура нужна, чтобы на них отвечать?

## Цели

- понимать роли в data-команде и место DE
- сформулировать бизнес-вопросы к FreshRetail
- нарисовать целевую архитектуру своего решения

## Темы

- роли: DA, BI, AE, DE, DS, ML Eng — границы и пересечения
- Modern Data Stack: ingestion → storage → transform → orchestration → serving
- ETL vs ELT, lakehouse vs warehouse, batch vs streaming
- архитектура аналитического решения (слои bronze/silver/gold)
- рынок: что требуют в вакансиях

## Инструменты

Mermaid (диаграммы в markdown), DuckDB для первичного EDA

## Лабы

Каждая лаба — папка `labs/<номер>_<название>/` с README по [шаблону](../../templates/lab_README.md).

- [ ] 01.1 — EDA датасета: гранулярность, ключи, пропуски, иерархии
- [ ] 01.2 — 5–10 бизнес-вопросов (out-of-stock, промо, погода, города, категории)
- [ ] 01.3 — архитектурная диаграмма и обзор вакансий

## Мини-проект (вклад в capstone)

`capstone/README.md` (вопросы) + `capstone/architecture.md` (схема) + `interview/market.md`.

## Ресурсы

- [Data-Learn: модуль 1 — роль аналитики](https://github.com/Data-Learn/data-engineering/blob/master/DE-101%20Modules/Module01/readme.md)
- [Fundamentals of Data Engineering (Reis, Housley) — гл. 1–3](https://www.oreilly.com/library/view/fundamentals-of-data/9781098108298/)

## Заметки

Конспект и выводы — в [`notes.md`](notes.md).
