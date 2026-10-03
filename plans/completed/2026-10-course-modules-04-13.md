---
title: Материалы модулей 04–13
status: completed
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
| 06 Оркестрация | слой `orchestration.yaml`: Dagster (+ Airflow опц.) | ✅ |
| 07 Spark | слой `spark.yaml`: master + 2 workers, Iceberg runtime | ✅ |
| 08 Стриминг | слой `streaming.yaml`: Redpanda, Console, Connect/Debezium, Flink; `wal_level=logical` | ✅ |
| 09 Качество | Soda Core, Elementary в зависимостях | ✅ |
| 10 Витрины | слой `serving.yaml`: ClickHouse, Trino, Superset, Evidence | ✅ |
| 11 Governance | слой `governance.yaml`: OpenMetadata | ✅ |
| 12 DataOps | pre-commit, шаблон GitHub Actions, Terraform в контейнере | ✅ |
| 13 Snowflake (опц.) | — (облако); `dbt-snowflake` в группе `cloud` | ✅ |

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

- 2026-10-02 — модуль 06, проверки на стеке: Dagster 1.13.25 в compose (webserver, daemon,
  code-сервер через `extends`, история в Postgres `dagster`). Порт 3000/3001 на хосте заняты
  (`secure_firefox`) → UI на 3070. Замеры и находки для уроков:
  - запуск «файл + bronze + проверка» ~25 с при ~1 с работы (процесс на шаг); backfill 3 дней —
    89 с, 7 дней — 176 с; dbt-шаг ~7 с;
  - ретраи `delay=2, EXPONENTIAL`: паузы 2 → 6 → 14 с;
  - проверка без пула → `Could not set lock on file` в 3 из 7 запусков backfill; с `pool="duckdb"` — 0;
  - сенсор не видел перезапись файла: fsspec переиспользует `S3FileSystem` с кэшем списков →
    `skip_instance_cache=True`;
  - `build_schedule_from_partitioned_job` с `end_date`: тик 2024-04-02 → партиция 04-01, тик в
    2026 → последняя партиция 2024-07-02;
  - блокирующая проверка смотрит на весь ассет: порча 04-02 остановила запуск за 04-01;
  - Airflow 3.3.2: `base_url` с хостовым портом → задачи не достучались до Execution API
    (`Connection refused`, SIGKILL); UID 50000 → `PermissionError` на томе; Asset-триггер работает.
- 2026-10-02 — **модуль 06 готов**: 5 уроков, 5 лаб (06.1–06.5), учебные проекты `demo/` (Dagster +
  dbt_weather) и `airflow_demo/`, 10 терминов, карточки, 5 карт, домашка (ключи — в памяти
  ассистента), README, infra/README, stack.md. Заранее добавлены группы зависимостей spark,
  streaming, quality. Следующий — модуль 07 (Spark).
- 2026-10-02 — модуль 07, проверки на стеке: Spark 4.1.3 standalone + Spark Connect (driver в
  `spark-connect`), клиент `pyspark-client` без JVM; Iceberg 1.12 через Lakekeeper с vended
  credentials. Проблемы слоя: произвольный UID без `/etc/passwd` → `user.home=?` (Ivy) и
  `Invalid UID` (Hadoop) → пользователь dev с UID хоста в образе; Python 3.10 в образе → 3.12 для UDF.
  Замеры для уроков:
  - train.parquet (106 МБ) — 4 задачи чтения; groupBy по магазинам: shuffle 38 КБ (901 строка),
    AQE 200 → 1 задача; repartition(8) — 4,5 млн строк через shuffle; почасовые 108 млн → магазин ×
    час: shuffle 402 КБ, ~1 с;
  - город 0 — 51,62 % строк. Sort-merge почасовых × города: 12 с, shuffle 193 МБ, задачи 4,2/9,1 с,
    spill 188 МБ; соль 8 — 9,8 с, 4,1/4,3 с; broadcast — 1,1 с. AQE skew join не сработал даже с
    порогом 16 МБ и force;
  - join с `distinct`-справочником: explain — SortMergeJoin, итоговый план — BroadcastHashJoin;
  - Iceberg: hash-распределение — файл на день; none + repartition(8) — 59 файлов по 36 КБ →
    компактизация 56 → 7; MERGE одного магазина-дня — 1 файл; expire_snapshots без older_than — 0;
    `CREATE OR REPLACE` — один коммит поверх истории;
  - движки, почасовые 108 млн → магазин × час: DuckDB 0,52 с / 376 МБ; Polars lazy 1,84 с / 5,5 ГБ;
    Spark 1,46 с (клиент 160 МБ, кластер ~5,5 ГБ); `coalesce(1)` → чтение 1 задачей, 2,7 с.
- 2026-10-02 — **модуль 07 готов**: 6 уроков, 5 лаб (07.1–07.5), демо (`spark_demo`, 6 тестов chispa,
  `bench_hourly.py`), 9 терминов, карточки, 6 карт, домашка (ключи — в памяти ассистента), README,
  infra/README, stack.md. Следующий — модуль 08 (стриминг).
- 2026-10-02 — модуль 09, проверки на стеке: Soda Core 4.25 + soda-duckdb (контракты YAML; раздел
  `columns` обязателен; `data-source create` знает только Postgres; коды выхода 0/1/2/3; Python API:
  `from_existing_cursor` с `ATTACH` и `data_timestamp`), Elementary 0.26 (пакет + `edr report`, схема
  `main_elementary`), dbt `contract: enforced`. Учебная база `demo_quality.duckdb` со сдвигом дат к
  «вчера»: детекторы и свежесть считают окна от текущего времени. Замеры и находки:
  - инциденты `--drop-day --null-city 3 --negative 2`: dbt FAIL 2 / 1 / 3, PASS=35 ERROR=3 SKIP=3;
    Soda — 3 провала, код 1; Elementary: `The last row_count value is 376.000. The average … 880.600`;
  - `--stale 2` → WARN, `--stale 3` → ERROR STALE в `dbt source freshness`;
  - переименование колонки → Soda schema FAILED + ошибка запроса → код 3 (не 1!);
  - на чистых данных 34 магазино-дня с продажами при нуле часов наличия (окно 6–22) — warn, не fail;
  - задержка загрузки: среднее 3,7 ч, p50 2,8, p95 13,6, в SLO «≤ 6 ч» — 93,8 % дней;
  - `--dupes`: +50 000 строк товаров, +1,122 % продаж против исходных файлов; dbt — FAIL 898
    уникальности + аномалия объёма, витрина SKIP.
- 2026-10-02 — **модуль 09 готов**: 5 уроков, 4 лабы (09.1–09.4), демо (`build_demo_db.py`, `soda/`,
  `dbt_quality/`), 6 терминов, карточки, 5 карт, домашка (ключи — в памяти ассистента), README.
- 2026-10-02 — модуль 08, проверки на стеке: Redpanda 26.2.3 + Console 3.12, Debezium 3.7.0,
  Flink 2.1.3 (свой образ), `wal_level=logical`. Находки и замеры:
  - demo-producer: 2694 события за 3 дня (898 × 3), партиции 825 / 663 / 1206; группы: lag 2684
    после 10 прочитанных; Avro: субъект `demo.weather_readings.avro-value`, ID 1, байты `00 00 00
    00 01`; совместимость: поле с default — True, переименование — False;
  - Debezium: снапшот `op=r`; без `REPLICA IDENTITY FULL` у UPDATE `before=null` → Flink
    `debezium-json` бесконечно перезапускается; офсеты коннектора переживают удаление (`Last
    recorded offset is no longer available`) → `PUT stop` + `DELETE offsets`; retained_wal ~3 КБ;
  - Flink: окна по дням — город 0 290 показаний; опоздавшие при переигрывании 3 партиций не
    теряются (минимум watermark + выпуск раз в 200 мс), на топике с 1 партицией и `on-event` —
    257 / 260 вместо 290; поток в Iceberg: 36 → 72 строки, 1 → 2 снапшота, 8 чекпоинтов;
  - INSERT в SQL-клиенте асинхронный (`table.dml-sync` для синхронного).
- 2026-10-02 — **модуль 08 готов**: 5 уроков, 5 лаб (08.1–08.5), демо (producer/consumer, Flink SQL,
  песочница CDC), 10 терминов, карточки, 5 карт, домашка (ключи — в памяти ассистента), README,
  infra/README, stack.md. Модули 06–09 закрыты; следующий — модуль 10 (витрины и BI).
- 2026-10-03 — модуль 10, проверки на стеке: ClickHouse 26.8.15.10, Trino 483, Superset 6.1.0
  (свой образ с драйверами), Evidence 40.1.8 (открытый фреймворк; шаблон теперь ведёт в Evidence
  Studio), MetricFlow 0.15 (группа `serving`). Находки и замеры:
  - почасовые продажи в ClickHouse: 116,4 млн строк из Parquet за 6,7 с; 2,28 ГиБ → 142,5 МиБ;
    `store_id = 348` — 28 гранул из 14 211, день — 37,2 млн строк (вся партиция); ключ с даты —
    день 147 гранул, магазин 213, размер 204,5 МиБ (+43 %);
  - 2 вставки → 10 частей; две мелкие части за 10 с не слились, 20 частей — за 8 с;
  - MV: 0 после создания, 194 строки до слияния, 97 с FINAL; ReplacingMergeTree — 1 796 → 898;
  - ClickHouse по Iceberg (`DataLakeCatalog`) — медиана 29 мс, копия MergeTree — 4 мс; Trino →
    Iceberg 113 мс, Trino → ClickHouse 65 мс (от клиента);
  - Trino: фильтр статуса уходит в Postgres (3 строки), динамический фильтр режет Iceberg
    1,53 млн → 5 580; `lower(status)` отключает pushdown (898 строк); агрегат уходит в ClickHouse;
  - MetricFlow: доля без товара 19,75 % = Superset = Evidence; без `alias` ratio с фильтром = 1;
  - Evidence: DATE/TIMESTAMP из Trino → `Cannot convert … to a BigInt`, срез `✖`, но «Done!»;
    сборка 87 МБ (DuckDB WASM), данные 41 КБ; `npm run build` рядом с `dev` ломает сборку →
    `make report`;
  - ClickHouse entrypoint делает `chown -R` у `user_files_path` → `CLICKHOUSE_DO_NOT_CHOWN=1`;
    `make logs` без `--profile '*'` не видел сервисы с зависимостями из других профилей.
- 2026-10-03 — **модуль 10 готов**: 7 уроков, 5 лаб (10.1–10.5), демо (`build_serving_demo.py`,
  `clickhouse/`, `dbt_semantic/`, `evidence_report/`), страница `mergetree_index.html`, 12 терминов,
  карточки, 7 карт, домашка (ключи — в памяти ассистента), README, infra/README, stack.md. Видео не
  делаем (решение пользователя). Следующий — модуль 11 (governance).
- 2026-10-03 — модуль 11, проверки на стеке: OpenMetadata 2.0.3 + Elasticsearch 9.3 на нашем
  Postgres; сбор Trino — 12 записей за ~1 с (+30 с старт контейнера); dbt-trino строит модели в
  Iceberg (87 106 / 898 / 1 746 строк). Сквозной граф собран: `raw_sales → [Spark] →
  store_sales_daily → stg → mart → модель Superset → дашборд`, плюс `postgresql.stores → stg_stores`.
  Находки — в stack.md (OpenLineage) и в уроках: владельцы dbt только для существующих команд;
  дашборд Superset без `position_json` попадает в каталог без чартов; одна таблица через два
  сервиса — два узла. Доступы: Trino-маска и фильтр (партнёр — `NULL`, менеджер — 97 строк),
  Postgres RLS (роль без политики — 0 строк без ошибки; владелец обходит).
- 2026-10-03 — **модуль 11 готов**: 4 урока, 3 лабы (11.1–11.3), демо (Spark + OpenLineage,
  dbt_governance, Superset, конфиги сбора, `om_demo_setup.py`, `emit_lineage.py`), 6 терминов,
  карточки, 4 карты, домашка (ключи — в памяти ассистента), README, infra/README, stack.md.
- 2026-10-03 — модуль 12, решение пользователя: CI — под отдельный репозиторий курса
  (`memory/decisions/ci-separate-repo.md`). Проверки на стеке: pre-commit на копии курса с `.git`
  — 17 с по всем файлам, хук `.env` срабатывает, Obsidian-файлы исключены из `end-of-file-fixer`;
  `make ci` — lint/test/dbt зелёные (7 мин 16 с первый раз; test — `6 skipped`); slim CI после
  правки одной витрины — 6 узлов из 16; actionlint — 0 ошибок. Terraform: Silo + Postgres, state в
  `tfstate`, цикл plan/apply/No changes/destroy; дрейф — `2 to add`.
- 2026-10-03 — **модуль 12 готов**: 5 уроков, 4 лабы (12.1–12.4), demo/terraform_local, CI-скрипты и
  workflow, `.pre-commit-config.yaml`, 4 термина, карточки, 5 карт, домашка (ключи — в памяти
  ассистента), README, infra/README, stack.md.
- 2026-10-03 — **модуль 13 готов** (опционально): 3 урока, 3 лабы, демо (SQL загрузки, dbt-проект под
  Snowflake), термин, карточки, 3 карты, домашка. На стеке проверены только `dbt-snowflake` 1.12.1,
  `dbt parse` и `dbt ls` без аккаунта (пустые переменные окружения → `or 'not-set'` в профиле);
  SQL Snowflake — по документации, помечено в уроках.

## Результат

Все модули 04–13 наполнены: уроки по шаблону (STE — 0 длинных предложений по новым модулям),
лабы с DoD и Steps, карточки, карты, глоссарий, домашки (ключи — в памяти ассистента), README с
маршрутами. Инфраструктура: слои `ingestion`, `orchestration`, `spark`, `streaming`, `serving`
(ClickHouse, Trino, Superset, Evidence), `governance` (OpenMetadata, OpenLineage), pre-commit,
CI (`make ci`, workflow под отдельный репозиторий), Terraform (`make tf`). Все «Попробуй сам»
модулей 04–12 прогнаны на стеке; модуль 13 — частично (облако).

Открытые вопросы: вынос курса в отдельный репозиторий (лаба 12.1) включит CI на GitHub; видео к
модулям 10–13 не делались (решение пользователя для модуля 10).
