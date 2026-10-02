# Лаба 08.3 · Debezium: CDC `retail_oltp` → Kafka → Iceberg

**Модуль:** [08 · Стриминг и CDC](../../README.md) · **Дата начала:** YYYY-MM-DD · **Статус:** ⬜

## Objective

Заменить выгрузку справочников по курсору `updated_at` (модуль 04) на CDC из журнала Postgres и
доказать на генераторе изменений, что CDC не теряет то, что терял курсор. Результат — текущие
справочники и их история в Iceberg, обновляемые потоком.

## Key Terms

_(заполни своими словами)_

- **WAL, логическая репликация, слот, публикация** —
- **Событие Debezium: before, after, op, tombstone** —
- **REPLICA IDENTITY** —
- **Двойственность потока и таблицы** —

## Prerequisites

- Теория: [03 · CDC](../../theory/03_cdc_debezium.md), [04](../../theory/04_time_windows_flink.md)
  (шаг 5), [05](../../theory/05_state_exactly_once_iceberg.md)
- Лабы 04.2–04.3: база `retail_oltp` и генератор `scripts/retail_oltp_changes.py`

## Tasks

### Task 1. Коннектор

**Expected result / Definition of Done:**
- Коннектор Debezium на `stores`, `products`, `assortment` базы `retail_oltp`; конфиг —
  `capstone/streaming/connect/retail_oltp.json`, секретов в нём нет
- Статус `RUNNING`; топики трёх таблиц; число событий снапшота = число строк в таблицах (сверка)
- Решение по `REPLICA IDENTITY` для каждой таблицы в README

### Task 2. CDC против курсора

**Expected result / Definition of Done:**
- `retail_oltp_changes.py --changes 20 --seed 1`; в README — таблица: операция генератора →
  увидел ли её курсор `updated_at` (модуль 04) → увидел ли её CDC (событие и `op`)
- Долгая транзакция (`--slow-tx`): когда пришло событие и с каким временем; почему CDC её не
  теряет

### Task 3. Справочники в Iceberg

**Expected result / Definition of Done:**
- Задание Flink (или consumer на Python — обоснуй выбор) держит в Iceberg **текущее** состояние
  `stores` по CDC: после генератора в режиме `--loop` таблица совпадает с `retail_oltp` (сверка)
- Удаление строки в источнике удаляет её из текущей таблицы

### Task 4. Эксплуатация слота

**Expected result / Definition of Done:**
- Эксперимент: коннектор остановлен на время работы генератора в `--loop` — рост
  `retained_wal` измерен запросом; после запуска коннектор догнал изменения без потерь
- Порядок полной уборки (коннектор → слот → публикация) записан и проверен на копии

## Результат

_(конфиг, таблица CDC против курсора, сверки, график retained_wal)_

## Выводы и вопросы

- Когда курсор `updated_at` всё же проще и достаточен?
