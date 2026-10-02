# Лаба 06.4 · (опц.) Тот же pipeline на Airflow 3

**Модуль:** [06 · Оркестрация](../../README.md) · **Дата начала:** YYYY-MM-DD · **Статус:** ⬜

## Objective

Перенести ежедневную загрузку продаж и сборку витрин capstone на Airflow 3 и сравнить на своём
pipeline task- и asset-подход. Результат — обоснованное решение, какой оркестратор взял бы для
сети и почему.

## Key Terms

_(заполни своими словами)_

- **DAG, task, TaskFlow, XCom** —
- **Логическая дата, data interval, catchup** —
- **Airflow Asset** —

## Prerequisites

- Теория: [05 · Airflow 3 для сравнения](../../theory/05_airflow_comparison.md)
- Лабы 06.1–06.3
- `make up PROFILES="airflow"`

## Tasks

### Task 1. Образ Airflow с инструментами capstone

**Expected result / Definition of Done:**
- `infra/docker/airflow/Dockerfile` ставит то, что нужно твоим задачам (dlt, dbt-duckdb и т. п.)
  с теми же версиями, что в `uv.lock`; версии указаны явно
- `airflow dags list-import-errors` — пусто; образ собирается `docker compose … build airflow`

**Steps:**
1. Где в `uv.lock` найти точные версии пакетов?
2. Почему нельзя просто поставить «последние» версии (модуль 00: фиксированные версии)?

### Task 2. DAG загрузки и витрин

**Expected result / Definition of Done:**
- DAG загрузки продаж за логическую дату (дата — параметр, не «сегодня») и сборки dbt;
  ретраи; один run одновременно
- `dags test` за два дня; повтор того же дня не создаёт дублей (запрос)
- Сборка витрин запускается по Airflow `Asset`, а не по времени

### Task 3. Сравнение

**Expected result / Definition of Done:**
- Таблица в README по пунктам: сколько кода, как задать день, как перезапустить день, как
  узнать, какие дни загружены, где видны тесты dbt, что пересчитать после сбоя, локальный
  запуск
- ADR «оркестратор для сети» в `capstone/architecture.md`: решение, альтернативы, последствия
- После сравнения — `docker compose --env-file .env -f infra/docker/compose.yaml stop airflow`

## Результат

_(DAG, таблица сравнения, ссылка на ADR)_

## Выводы и вопросы

- Какой вопрос о данных Airflow не смог ответить без запроса к самой таблице?
