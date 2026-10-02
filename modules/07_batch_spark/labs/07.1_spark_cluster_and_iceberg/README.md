# Лаба 07.1 · Кластер Spark и Iceberg через Lakekeeper

**Модуль:** [07 · Батч-обработка: Spark](../../README.md) · **Дата начала:** YYYY-MM-DD · **Статус:** ⬜

## Objective

Убедиться, что Spark видит тот же lakehouse, что dlt и dbt: читает bronze, записанный dlt,
пишет новую таблицу Iceberg, а её читает DuckDB. Навык — разобрать слой Spark по сервисам и
доказать совместимость движков на одних таблицах.

## Key Terms

_(заполни своими словами)_

- **Driver, executor, worker, менеджер кластера** —
- **Spark Connect** —
- **Vended credentials** —
- **Распределение записи Iceberg** —

## Prerequisites

- Теория: [01 · Модель выполнения](../../theory/01_execution_model.md),
  [04 · Spark и Iceberg](../../theory/04_spark_iceberg.md)
- `make up PROFILES="spark"`; bronze из модуля 04 (лаба 04.6) в Iceberg

## Tasks

### Task 1. Слой spark по сервисам

**Expected result / Definition of Done:**
- Таблица в README: сервис → роль → откуда его настройки (файл и строка) → порты → что
  перестанет работать, если его остановить
- Предсказание и проверка: что произойдёт с запросом, если во время него остановить
  `spark-worker-2` (`docker stop`)? Что видно в UI 8090 и 4040, чем закончился запрос

**Steps:**
1. Где задано, сколько ядер и памяти получит приложение? А сколько есть у workers?
2. Проверка «остановить worker» — на запросе, который идёт 10+ секунд (урок 03).

### Task 2. Чтение bronze, записанного dlt

**Expected result / Definition of Done:**
- Spark читает таблицу продаж bronze из Iceberg (`lh.<namespace>.<таблица>`); число строк и сумма
  `sale_amount` совпадают с подсчётом DuckDB по той же таблице (оба запроса в `queries.sql`)
- В README: какие служебные колонки dlt видны в Spark и откуда они

### Task 3. Запись из Spark, чтение из DuckDB

**Expected result / Definition of Done:**
- Spark создаёт в namespace `silver` таблицу продаж по дням с партиционированием по дню
  (схема и выбор колонок — твои), атомарно (`createOrReplace`)
- DuckDB (`ATTACH … TYPE iceberg`) читает её; сверка строк и сумм — в `queries.sql`
- `t.files`: число файлов на день; объясни его через `write.distribution-mode`

## Результат

_(таблица сервисов, сверки Spark ↔ DuckDB)_

## Выводы и вопросы

- Что из модуля 05 (публикация витрин DuckDB) ты теперь сделал бы Spark'ом и почему?
