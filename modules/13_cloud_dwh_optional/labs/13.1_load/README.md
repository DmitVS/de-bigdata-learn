# Лаба 13.1 · Загрузка датасета в Snowflake

**Модуль:** [13 · Облачное хранилище](../../README.md) · **Дата начала:** YYYY-MM-DD · **Статус:** ⬜

## Objective

Завести trial-аккаунт Snowflake, загрузить FreshRetailNet-50K и проверить, что данные совпадают с
lakehouse. Тренируем склады, stage, `COPY INTO` и контроль расходов с первого дня.

## Key Terms

_(заполни своими словами)_

- **Виртуальный склад, кредит, автоостановка** —
- **Stage, `COPY INTO`, журнал загрузок** —
- **Микропартиция, отсечение** —

## Prerequisites

- Аккаунт Snowflake (trial, 30 дней)
- Реквизиты — в `.env`: `SNOWFLAKE_ACCOUNT`, `SNOWFLAKE_USER`, `SNOWFLAKE_PASSWORD`, `SNOWFLAKE_ROLE`
- Теория: [01 · Архитектура](../../theory/01_snowflake_architecture.md),
  [02 · Загрузка и dbt](../../theory/02_load_and_dbt.md)
- Образец: `demo/snowflake/01_setup_and_load.sql`

## Tasks

### Task 1. Аккаунт и контроль расходов

**Expected result / Definition of Done:**
- Склад `XSMALL` с `AUTO_SUSPEND = 60`; ресурсный монитор с лимитом кредитов на месяц и
  оповещением на 75 % (команды — в README)
- В README — сколько кредитов потрачено за всю лабу (запрос к `ACCOUNT_USAGE` или экран Admin → Cost)

### Task 2. Загрузка

**Expected result / Definition of Done:**
- Файлы датасета в stage, таблица `raw.sales` создана по схеме Parquet и загружена
- Сверка с lakehouse: число строк (4 850 000), диапазон дат, сумма `sale_amount` — совпадают с
  запросом в DuckDB или Trino; запросы и числа в README
- Повторный `COPY INTO` ничего не загрузил; в README — почему

**Steps:**
1. Положи файлы в stage (Snowsight или `PUT` из Python-коннектора в `make shell`).
2. Выполни образец, сверяясь с документацией; каждое отличие от образца объясни.

### Task 3. Отсечение

**Expected result / Definition of Done:**
- Запрос с фильтром по дню: в Query Profile — Partitions scanned / Partitions total; скриншот
- Ответ в README: почему отсечение такое, и что изменится, если загрузить файлы в другом порядке

## Результат

_(расход кредитов, сверка, Query Profile)_

## Выводы и вопросы

- Что в Snowflake оказалось проще, чем в нашем стеке, а что — сложнее?
