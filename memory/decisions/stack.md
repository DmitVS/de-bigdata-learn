---
name: stack
description: Выбор компонентов и версий стека; почему Silo вместо MinIO; зарезервированные порты
metadata:
  type: decision
---

Состояние на 2026-09-23 (слой core):

| Компонент | Образ | Почему |
|---|---|---|
| S3 | `pgsty/silo:RELEASE.2026-09-03T13-18-01Z` | community-образы MinIO убраны с Docker Hub; Silo — поддерживаемый форк MinIO с STS, официальный пример Lakekeeper использует его |
| Iceberg-каталог | `quay.io/lakekeeper/catalog:v0.13.6` | REST-каталог на Rust, выдаёт временные S3-ключи (vended credentials), UI |
| Postgres | `postgres:17.11` | метаданные Lakekeeper + `retail_oltp` |
| Workspace | `ghcr.io/astral-sh/uv:python3.12-bookworm-slim` + DuckDB CLI 1.5.5 | Python 3.12 — самая совместимая версия для dbt/Spark/Airflow |

Альтернативы: RustFS 1.0 (S3), Apache Polaris / iceberg-rest-fixture (каталог).

Порт 8080 на хосте занят (open-webui). Для будущих слоёв зарезервированы порты в `infra/README.md`.
Версии фиксируются явно; обновление — осознанно, с записью здесь.

## Дополнение от 2026-10-01: pyiceberg-core

В `pyproject.toml` к `pyiceberg` добавлен extra `pyiceberg-core` (в lock — `pyiceberg-core 0.10.1`).
Без него PyIceberg 0.12 не вычисляет преобразования партиций (`month`, `day`, `bucket` …) и падает с
`NotInstalledError` при записи в партиционированную таблицу. Нужно для модуля 03 (скрытое
партиционирование). Образ workspace пересобран, `make check` — OK.

## Дополнение от 2026-10-01: модуль 04 (ingestion)

- **Образ workspace ставит все группы зависимостей** (`uv sync --all-groups`): иначе пакеты,
  добавленные `make uv ARGS="add --group <модуль> …"`, не попадали в образ. pandas 3 — группа
  `ingestion`.
- **dlt пишет Iceberg через REST-каталог Lakekeeper** (dlt 1.30: `filesystem` +
  `table_format="iceberg"`, каталог из `ICEBERG_CATALOG__ICEBERG_CATALOG_CONFIG`). Ограничения,
  проверенные на стеке: путь только внутри `s3://warehouse/lakehouse/`; стратегии merge —
  только `upsert` и `insert-only`; upsert идёт пачками по 1 000 строк с коммитом на каждую
  (100 тыс. строк → ~98 с, 100 снапшотов). Поэтому в курсе: справочники — replace или merge,
  факты — append с защитой от повторов.
- **Учебные источники — свои эмуляторы, а не внешние сервисы**: `retail-api` (слой
  `ingestion.yaml`, на образе workspace, stdlib + DuckDB) даёт воспроизводимые 401/429/503 и
  курсорную пагинацию; `landing_drop.py` и `retail_oltp_changes.py` эмулируют файлы и учётную
  систему. Публичный API — только Nager.Date (праздники), для сверки с `holiday_flag`.

## Дополнение от 2026-10-01: модуль 05 (dbt)

- **dbt строит модели в файле DuckDB, а не в Iceberg.** DuckDB 1.5 для Iceberg не умеет
  `CREATE OR REPLACE`, представления и переименование таблицы, изменённой в той же транзакции;
  материализация `table` dbt-duckdb падает («…__dbt_tmp was modified already, can't be
  renamed»). Bronze читается из Iceberg через `attach` в профиле (`type: iceberg`), готовые
  витрины публикуются в Iceberg post-hook'ом `DROP` + `CREATE TABLE AS` с `transaction: false`
  (одна транзакция DuckDB пишет только в одну базу). Публикация неатомарна — приемлемо для
  учебного стека; атомарная замена — Spark (модуль 07).
- SQLMesh 0.228 — группа зависимостей `transform`; порт 8580 у workspace для `dbt docs serve`.

## Дополнение от 2026-10-02: модуль 06 (оркестрация)

- **Dagster 1.13.25** (dagster-dbt, dagster-dlt, dagster-postgres 0.29.25) — группа
  `orchestration`, ставится в образ workspace. Слой `orchestration.yaml`: webserver, daemon и
  отдельный **code-сервер** на каждый проект (gRPC, `dagster code-server start`), а не
  `dagster dev`: так устроен продакшен, и код проекта изолирован от оркестратора. Code-сервер
  наследует окружение workspace через `extends` + `build: !reset null` + `ports: !reset []`.
- **История — в Postgres** (база `dagster`, создаётся однократным сервисом `dagster-db-init`), а
  не в SQLite: три контейнера должны видеть одну историю.
- **Пул `duckdb` с лимитом 1** (`concurrency.pools`): файл DuckDB — один писатель, а читатель тоже
  берёт блокировку; без пула у читающей проверки backfill падал `Could not set lock on file`.
- **Порт UI 3070**: 3000 и 3001 на хосте заняты контейнером `secure_firefox`. Evidence (модуль 10)
  перенесён в резерв на 3071.
- **Airflow 3.3.2** — только для сравнения: свой образ `debd/airflow:3.3.2` (+ DuckDB 1.5.5),
  `standalone` на SQLite, профиль `airflow`, порт 8081. Работает от `HOST_UID:0`; адрес Execution API
  задан явно (`http://localhost:8080/execution/`), иначе Airflow выводил его из хостового порта.
- Заранее добавлены группы следующих модулей (одна пересборка образа): `spark`
  (pyspark-client 4.1.3 — Spark Connect без JVM, chispa 0.12), `streaming`
  (confluent-kafka 2.15 с avro и schema registry), `quality` (soda-core 4.25 + soda-duckdb,
  elementary-data 0.26 с duckdb).

## Дополнение от 2026-10-02: модуль 07 (Spark)

- **Spark 4.1.3 standalone + Spark Connect.** Driver — долгоживущий сервер `spark-connect`, клиент
  в workspace — `pyspark-client` (чистый Python, без JVM). Так в workspace не нужны Java и JAR-файлы,
  UI приложения (4040) живёт долго и годится для разбора запросов. Цена: нет RDD API.
- **Свой образ `debd/spark:4.1.3`**: Iceberg 1.12.0 (`iceberg-spark-runtime-4.1_2.13`,
  `iceberg-aws-bundle`) в `jars/`, Python 3.12 (uv) для executors, пользователь dev с UID хоста.
- **Iceberg через REST-каталог с vended credentials** — ключей S3 нет в конфиге Spark.
- Ресурсы: 2 workers × (2 ядра, 3 ГБ), executor 2 ядра / 2 ГБ, driver 2 ГБ; всего ~5,5 ГБ RAM.
  Порты: 8090 (master UI), 4040 (UI приложения).

## Дополнение от 2026-10-02: модуль 09 (качество)

- **Soda Core 4.25** (+ soda-duckdb) — контракты источника и bronze; коды выхода 0/1/2/3, ворота в
  Dagster — по коду, где 3 тоже провал. Для Iceberg и исторических дат — Python API
  (`from_existing_cursor` + `ATTACH`, `data_timestamp`).
- **Elementary 0.26** — dbt-пакет и CLI `edr` в одной версии; служебные таблицы в `main_elementary`.
  Детекторы аномалий считают окна от текущей даты → учебная база модуля сдвигает даты датасета к
  «вчера» (значения не меняются).
- Great Expectations — только в теории (сравнение), в образ не ставится.

## Дополнение от 2026-10-02: модуль 08 (стриминг)

- **Redpanda v26.2.3** вместо Apache Kafka: один бинарник, Schema Registry и HTTP-прокси
  встроены, режим `dev-container`, 1 ГБ памяти. Console v3.12.0 — UI на 8084.
- **Debezium 3.7.0.Final** (`quay.io/debezium/connect`) — Kafka Connect с коннекторами; секреты из
  окружения через `EnvVarConfigProvider`. Postgres переведён на `wal_level=logical`.
- **Flink 2.1.3** — свой образ с Kafka 5.0.0-2.1, Avro Confluent 2.1.3, Iceberg 1.12 (runtime 2.1,
  AWS bundle) и Hadoop client 3.4.3 (Iceberg для Flink использует классы конфигурации Hadoop);
  каталог Iceberg — тот же REST Lakekeeper с vended credentials. UI на 8086 (8081 занят Airflow).
- Проверено на стеке: Flink `debezium-json` падает на UPDATE с `before: null` → таблицам CDC нужен
  `REPLICA IDENTITY FULL`; офсеты коннектора переживают его удаление; при быстром переигрывании
  топика с несколькими партициями опоздание не проявляется (минимум watermark по партициям +
  периодический выпуск) — демо опоздавших на топике с одной партицией и `on-event`.
- Образы слоя большие (Flink ~1 ГБ); на канале ~0,3 МБ/с первая загрузка заняла ~40 мин —
  BuildKit при этом «зависал» без вывода, отдельный `docker pull` помог.

## Дополнение от 2026-10-03: слой media (видео-объяснения)

- Образ `debd/media:local`: база `ghcr.io/astral-sh/uv:python3.12-bookworm-slim`, Manim 0.21.0,
  manim-voiceover 0.4.0, piper-tts 1.8.0 с голосом `ru_RU-ruslan-medium` (встроен в образ). Версии
  закреплены в `infra/docker/media/requirements.txt` — отдельно от `uv.lock`: системные библиотеки
  Manim (cairo, pango) не нужны в workspace. Сборка ролика 1:49 в 1080p60 — около 40 с.

## Дополнение от 2026-10-03: модуль 10 (витрины и BI)

- **ClickHouse 26.8.15.10** (LTS) — копия витрин для дашборда. Iceberg читает движком базы
  `DataLakeCatalog` через REST Lakekeeper (beta, `allow_database_iceberg = 1`), ключи S3 — от
  каталога. Репозиторий смонтирован только на чтение, `user_files_path` = `data/`;
  `CLICKHOUSE_DO_NOT_CHOWN=1` обязателен — иначе entrypoint делает `chown -R` этой папки.
- **Trino 483** — федерация Iceberg + Postgres `retail_oltp` + ClickHouse; `mem_limit: 3g`
  (куча — 80 % лимита по настройке образа). Pushdown фильтров и агрегатов в JDBC-источники.
- **Superset 6.1.0** — свой образ: официальный образ без драйверов баз (psycopg2-binary,
  clickhouse-connect 1.9.0, trino 0.340.0 ставятся в `/app/.venv`). Метаданные — база `superset`
  в общем Postgres; без Redis и Celery (SimpleCache).
- **Evidence — открытый фреймворк `@evidence-dev/evidence` 40.1.8**, а не Evidence Studio: шаблон
  `evidence-dev/template` с 2026 года ведёт в облачный продукт с отдельным CLI и входом в
  аккаунт. Фреймворк закреплён с `typescript` 5.4.2 (иначе ERESOLVE с TypeScript 7). Коннектор
  Trino 1.0.11 не переносит DATE/TIMESTAMP — даты передаём строкой. Альтернатива — Quarto.
- **Семантический слой — dbt + MetricFlow 0.15** (`dbt-metricflow[dbt-duckdb]`, группа `serving`):
  open source даёт только CLI `mf`; API для BI — платный dbt Cloud, поэтому метрики Superset
  повторяют формулы и сверяются с `mf query`. Cube не ставим (ещё один сервис).
- Порты: 8123, 8082, 8088, 3071. Видео к модулю не делаем (решение пользователя 2026-10-03).

## Дополнение от 2026-10-03: модуль 11 (governance)

- **OpenMetadata 2.0.3** на общем Postgres 17 (база `openmetadata`) + **Elasticsearch 9.3.0**;
  встроенный Airflow не ставится — сбор метаданных CLI `metadata` в разовом контейнере
  `openmetadata/ingestion:2.0.3` по YAML в git (`make om-ingest`), `${…}` из окружения работают.
- **Lineage Spark — стандартный `openlineage-spark` 1.53.0** (в образе `debd/spark:4.1.3`) по HTTP
  на `/api/v1/openlineage/lineage`, а не агент OpenMetadata: стандарт важнее продукта.
  Находки: Java-клиент — адрес без пути, путь в `endpoint`; сервис пайплайнов `openlineage` и
  пайплайны создаются заранее (2.0.3 падает на `updatedat`); файлы не сопоставляются; lineage
  колонок из Spark не сопоставляется (входы — места в S3); Python-события — время с `Z`.
- **dbt-trino 1.10.6** (группа `governance`) для учебного проекта: модели в Iceberg через Trino,
  поэтому каталог связывает модели dbt с таблицами сервиса `trino_lake`. Capstone остаётся на
  dbt-duckdb.
- Правила доступа Trino — файл `trino/rules.json` (перечитывается каждые 10 с); последнее правило
  оставляет полный доступ остальным, чтобы не ломать модули 05–10.

## Дополнение от 2026-10-03: модуль 12 (DataOps)

- **pre-commit 4.6** в группе `dev` образа workspace; хуки ruff/sqlfmt/yamllint — `language: system`
  (одна версия из `uv.lock` для pre-commit, `make lint` и CI); git-хук на хосте вызывает `make`.
- **CI** — GitHub Actions под отдельный репозиторий курса ([ci-separate-repo](ci-separate-repo.md));
  шаги в `scripts/ci/*.sh`, локальная проверка `make ci` в чистом контейнере uv и actionlint 1.7.12.
  Версии: checkout v7, setup-uv v10.2.0 (короткого тега v10 нет — первый запуск на GitHub упал на `Set up job`; uv 0.9.30), cache v6, upload-pages-artifact v5, deploy-pages v5.
  Slim CI — `manifest.json` прода с GitHub Pages. Первый `make ci` — 7 мин (загрузка), dbt — 1,2 с.
- **Terraform 1.16.5** в контейнере; провайдеры `aminueza/minio` (~> 3.0) и `cyrilgdn/postgresql`
  (~> 1.25) управляют нашим же стеком; state в Silo (`tfstate`). Облачный вариант — только обзор:
  провайдер AWS ~0,5 ГБ и нужен аккаунт.

## Дополнение от 2026-10-03: модуль 13 (Snowflake, опционально)

- `dbt-snowflake` 1.12.1 — группа `cloud` образа workspace; реквизиты `SNOWFLAKE_*` из `.env`
  передаются в workspace (пустые по умолчанию). Без аккаунта работают `dbt parse` и `dbt ls`.
  Облачные команды в уроках помечены как проверенные по документации.
