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
