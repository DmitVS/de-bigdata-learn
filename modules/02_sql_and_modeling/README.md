# Модуль 02 · SQL и моделирование данных

**Длительность:** ~2 нед. · **Статус и DoD:** см. [ROADMAP](../../ROADMAP.md)

## Бизнес-вопрос

> Какая модель данных позволит быстро и однозначно отвечать на вопросы сети?

## Цели

- писать аналитический SQL уверенно
- спроектировать звёздную схему для FreshRetail
- понимать SCD и альтернативы Kimball

## Темы

- оконные функции, CTE, QUALIFY, GROUPING SETS, UNNEST массивов
- OLTP vs OLAP, нормализация vs денормализация
- Kimball: факты (транзакционные, периодические снимки), измерения, гранулярность
- SCD типов 0/1/2, Data Vault и One Big Table — обзор
- производительность: колоночное хранение, план запроса (EXPLAIN)

## Инструменты

DuckDB (CLI и Python), Postgres

## Лабы

Каждая лаба — папка `labs/<номер>_<название>/` с README по [шаблону](../../templates/lab_README.md).

- [ ] 02.1 — 15 задач по оконным функциям на продажах
- [ ] 02.2 — разворот `hours_sale` / `hours_stock_status` в почасовую гранулярность
- [ ] 02.3 — звёздная схема: ER-диаграмма и DDL
- [ ] 02.4 — EXPLAIN ANALYZE: одна и та же задача тремя способами

## Мини-проект (вклад в capstone)

SQL-ответы на 3 бизнес-вопроса из модуля 01 поверх своей звёздной схемы.

## Ресурсы

- [Data-Learn: модуль 2 — базы данных и SQL](https://github.com/Data-Learn/data-engineering/blob/master/DE-101%20Modules/Module02/readme.md)
- [The Data Warehouse Toolkit (Kimball) — гл. 1–4](https://www.kimballgroup.com/data-warehouse-business-intelligence-resources/books/data-warehouse-dw-toolkit/)
- [DuckDB SQL docs](https://duckdb.org/docs/stable/sql/introduction)

## Книга и видео

Полная таблица с пояснениями, зачем читать и что пропустить — в [карте чтения](../../reading_map.md#02--sql-и-моделирование-данных).

- 📖 Клеппман, гл. 2 — модели данных
- 📖 Клеппман, гл. 3 — OLTP vs OLAP, звезда и снежинка
- 🎬 [Zoomcamp `04-analytics-engineering`](https://github.com/DataTalksClub/data-engineering-zoomcamp/tree/main/04-analytics-engineering) — видео про моделирование данных

## Домашка-чекпоинт

После всех лаб — `homework.md` по [шаблону](../../templates/homework.md).

## Заметки

Конспект, тезисы по книге и выводы — в [`notes.md`](notes.md).
