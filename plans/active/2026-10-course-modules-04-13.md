---
title: Материалы модулей 04–13
status: active
created: 2026-10-01
type: infra
---

# Материалы модулей 04–13

## Цель

Подготовить теорию, лабы, карточки, карты, домашки и инфраструктуру для всех оставшихся модулей
курса в формате модулей 00–03 (AGENTS.md, правила 7–8). Каждая команда из «Попробуй сам»
проверяется на живом стеке. Лабы — задачи с DoD и Steps, без готовых решений.

## План действий

Порядок — по номерам модулей: каждый следующий опирается на инфраструктуру предыдущего.

| Модуль | Инфраструктура | Статус |
|---|---|---|
| 04 Ingestion | переменные dlt в workspace, `--all-groups` в образе, pandas; слой `ingestion.yaml` (учебный API `retail-api`); скрипты `landing_drop.py`, генератор изменений `retail_oltp` | ✅ |
| 05 dbt | учебные проекты `demo/` и `demo_sqlmesh/`, SQLMesh в группе `transform`, порт 8580 | ✅ |
| 06 Оркестрация | слой `orchestration.yaml`: Dagster (+ Airflow опц.) | ⬜ |
| 07 Spark | слой `spark.yaml`: master + 2 workers, Iceberg runtime | ⬜ |
| 08 Стриминг | слой `streaming.yaml`: Redpanda, Console, Connect/Debezium, Flink; `wal_level=logical` | ⬜ |
| 09 Качество | Soda Core, Elementary в зависимостях | ⬜ |
| 10 Витрины | слой `serving.yaml`: ClickHouse, Trino, Superset, Evidence | ⬜ |
| 11 Governance | слой `governance.yaml`: OpenMetadata | ⬜ |
| 12 DataOps | pre-commit, шаблон GitHub Actions, Terraform в контейнере | ⬜ |
| 13 Snowflake (опц.) | — (облако) | ⬜ |

Для каждого модуля: уроки `theory/`, лабы `labs/` (DoD + Steps), `flashcards.md`, `homework.md`
(ключи — только в памяти ассистента), карты `maps/*.canvas`, термины в `glossary/`, README с
маршрутом и чек-листом, правки `ROADMAP.md`, `infra/README.md`, `memory/decisions/`.

## Definition of Done

- У каждого модуля 04–13 есть уроки, лабы, карточки, карты, домашка и README с маршрутом
- Все «Попробуй сам» прогнаны на стеке; песочницы (`sandbox`, `zz_*`) удалены
- Новые слои поднимаются `make up PROFILES="…"`, `make check` зелёный
- Решения по инфраструктуре записаны в `memory/decisions/`

## Риски

- Ресурсы: 30 ГБ RAM. Слои поднимать по одному, governance — отдельно от spark/streaming.
- Версии образов и пакетов: проверять `docker pull` и запуском, а не по памяти.
- dlt пишет Iceberg через Lakekeeper только внутри `s3://warehouse/lakehouse/…` (проверено).

## Журнал

- 2026-10-01 — план составлен. Проверено: dlt 1.30 пишет Iceberg через REST-каталог Lakekeeper
  (append и merge, инкремент по курсору); `holiday_flag` = выходные + госпраздники КНР, с
  расхождениями в дни переносов — материал для лабы 04.4.
- 2026-10-01 — инфраструктура модуля 04 готова и проверена: образ ставит все группы
  (`--all-groups`), pandas 3.0.6 в группе `ingestion`; переменные dlt в workspace (секреты из
  `.env`, `DLT_DATA_DIR=data/.dlt`); слой `ingestion.yaml` с `retail-api` (порт 8095, ключ
  `RETAIL_API_KEY`); `scripts/landing_drop.py`; `scripts/retail_oltp_changes.py`.
  Замеры для уроков 04:
  - dlt `read_parquet` отдаёт строки-словари: 100 тыс. строк → 16,4 с, массивы → дочерние таблицы
    по 2,4 млн строк; свой трансформер с `pq.read_table` (Arrow) → 1,6 с, `list<>` сохраняются,
    int32 остаётся int, но нет `_dlt_load_id/_dlt_id`.
  - append + повторная доставка файла → 150 тыс. строк вместо 100 тыс. (дубли).
  - merge upsert в Iceberg: пачки по 1 000 строк, каждая — коммит: 100 тыс. строк → 100 файлов,
    100 снапшотов, ~96 с; повтор тех же данных — снова ~95 с, новых снапшотов нет.
    `delete-insert` для Iceberg не поддерживается (только `upsert`, `insert-only`).
  - sql_database, 3 справочника upsert: первая загрузка 166 с (52 тыс. строк); генератор
    `--changes 20 --seed 1` → инкремент взял 7 stores + 27 assortment, потерял 4 recategorize и
    2 delete. Долгая транзакция (`--slow-tx 15`) потеряна курсором; `lag=3600` её нашёл.
  - все строки с одинаковым значением курсора → dlt хранит хэши всех строк в state (раздувание).
  - RESTClient + JSONResponseCursorPaginator: 3 даты → 27 страниц, 5,4 с, 503 повторяются сами;
    `items` → дочерняя таблица `promotions__items` (`_dlt_parent_id`).
  - контракты: freeze → `DataValidationError` на шаге normalize; discard_value/discard_row
    работают; int → text в существующей колонке → вариантная колонка `city_id__v_text`.
  - движки, train.parquet, агрегат по магазину и дню: DuckDB 0,45 с / 507 МБ; Polars lazy
    0,50 с / 2,7 ГБ; Polars eager 0,74 с / 5,3 ГБ; pandas 7,25 с / 7,8 ГБ; pandas с columns
    5,97 с / 3,9 ГБ.
  - sql_database отражает PK из базы; replace трёх справочников в Iceberg — 1,9 с (повтор 1,3 с)
    против 166 с первой загрузки upsert.
  - Nager.Date 2024/CN: 6 праздников, в период датасета только 05-01 и 06-10 (нет Цинмина);
    `holiday_flag` = 33 дня. upsert с дочерней таблицей не удаляет ушедшие элементы списка.
  - DLT: `NORMALIZE__PARQUET_NORMALIZER__ADD_DLT_LOAD_ID=true` добавляет `_dlt_load_id` к Arrow.

- 2026-10-01 — **модуль 04 готов**: 6 уроков, 6 лаб (04.1–04.6), 15 терминов, карточки,
  6 карт, домашка (ключи — в памяти ассистента), README, ROADMAP, infra/README, stack.md.
- 2026-10-01 — модуль 05, проверки на стеке: dbt 1.12.5 + dbt-duckdb 1.11.0, SQLMesh 0.228.4
  (группа `transform`), порт 8580 для `dbt docs serve`/SQLMesh. DuckDB 1.5 + Iceberg: CTAS,
  INSERT, DELETE, UPDATE, MERGE, DROP — да; `CREATE OR REPLACE`, VIEW — нет; materialization
  `table` dbt в Iceberg падает («m_table__dbt_tmp was modified already, can't be renamed»);
  одна транзакция пишет только в одну базу → публикация в Iceberg post-hook'ом с
  `transaction: False` (DROP + CTAS) работает. Архитектура: dbt считает в DuckDB-файле, bronze
  читает через `attach` (type iceberg), публикует выбранные модели в Iceberg.
  Работают: sources `external_location`, unit tests, persist_docs (COMMENT), dbt_utils 1.4.1,
  snapshots в YAML + `hard_deletes: new_record` (`dbt_is_deleted`), microbatch — но с `begin`
  он идёт до сегодня (834 пачки, 143 с) → нужны `--event-time-start/--event-time-end`.
  SQLMesh: VIEW + INCREMENTAL_BY_TIME_RANGE, prod-план без `--end`; dev-окружение `demo__dev`;
  изменение классифицировано Non-breaking; выкатка в prod — «No physical layer updates».
- 2026-10-01 — **модуль 05 готов**: 6 уроков, 7 лаб (05.1–05.7), учебные проекты dbt и SQLMesh,
  9 терминов, карточки, 6 карт, домашка (ключи — в памяти ассистента), README, ROADMAP.
  Следующий — модуль 06 (оркестрация, слой `orchestration.yaml`).

## Результат

_(заполняется по завершении)_
