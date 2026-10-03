# Инфраструктура

Весь стек — Docker Compose, **только контейнеры**. На хосте: `docker` (compose v2) и `make`.
Проект compose называется `debd` (`docker ps` покажет контейнеры `debd-*`).

## Слои

`infra/docker/compose.yaml` подключает слои через `include`. Файл слоя создаётся в том модуле,
где слой впервые нужен, а его сервисы получают `profiles: [<слой>]`, чтобы не запускаться без
необходимости: `make up PROFILES="spark"`.

| Слой (файл) | Сервисы | RAM | Модуль | Статус |
|---|---|---|---|---|
| `core.yaml` | Postgres 17, Silo (S3), Lakekeeper, workspace | ~1,5 ГБ | 00–05 | ✅ |
| `ingestion.yaml` | `retail-api` — учебный API маркетинговой системы | ~0,3 ГБ | 04 | ✅ |
| `orchestration.yaml` | Dagster (webserver, daemon, code-сервер `dagster-demo`) — профиль `orchestration`; Airflow 3 standalone — профиль `airflow` | ~0,7 ГБ Dagster, ~1,2 ГБ Airflow | 06 | ✅ |
| `spark.yaml` | Spark master, 2 workers (по 2 ядра, 3 ГБ), Spark Connect (driver) — профиль `spark` | ~5,5 ГБ | 07 | ✅ |
| `streaming.yaml` | Redpanda (+ Schema Registry) + Console, Kafka Connect/Debezium, Flink (jobmanager + taskmanager) — профиль `streaming` | ~4–5 ГБ | 08 | ✅ |
| `serving.yaml` | ClickHouse 26.8, Trino 483, Superset 6.1 — профиль `serving`; Evidence — профиль `evidence` | ~3–4,5 ГБ (Trino ≤ 3 ГБ) | 10 | ✅ |
| `media.yaml` | `media` — Manim + Piper для видео-объяснений (запуск по `make video`, не сервис) | по вызову | все | ✅ |
| `governance.yaml` | OpenMetadata 2.0.3 + Elasticsearch 9.3, сбор `om-ingest`, `spark-lineage` — профиль `governance` | ~3 ГБ (+1 ГБ на время сбора) | 11 | ✅ |

Машина: Ryzen 7 9700X (16 потоков), 30 ГБ RAM, ~89 ГБ свободно на диске. Комфортная сессия —
core + 1–2 слоя. Governance запускать отдельно от spark/streaming.

## Слой core

```
            ┌──────────── workspace (Python 3.12: dbt, dlt, DuckDB, Polars, PyIceberg, Jupyter)
            │                   │ REST                        │ S3 (vended credentials)
            ▼                   ▼                             ▼
      postgres:5432 ◄── lakekeeper:8181 (Iceberg REST) ──► silo:9000 (бакеты landing, warehouse)
   (lakekeeper, retail_oltp)
```

- **postgres** — БД `lakekeeper` (метаданные каталога) и `retail_oltp` (учебная учётная система
  сети — источник для ingestion и CDC). Базы создаёт `postgres/init/01-databases.sql` при первом старте тома.
- **silo** — S3-хранилище, поддерживаемый форк MinIO (`pgsty/silo`). Официальные community-образы
  MinIO больше не публикуются на Docker Hub. `silo-init` создаёт бакеты `landing` и `warehouse`.
- **lakekeeper** — Iceberg REST-каталог. `lakekeeper-migrate` применяет миграции,
  `lakekeeper-init` (скрипт `lakekeeper/init.sh`) выполняет bootstrap и создаёт warehouse `lakehouse`.
  Клиенты получают от каталога временные S3-ключи (STS), поэтому им нужен только адрес каталога.
- **workspace** — рабочий контейнер; репозиторий смонтирован в `/workspace`, venv — в `/opt/venv`.
  Запускает JupyterLab; для терминала — `make shell`, для SQL — `make sql`.

## Порты (только 127.0.0.1)

| Порт | Сервис | Заметка |
|---|---|---|
| 5432 | Postgres | |
| 9000 / 9001 | Silo S3 API / консоль | |
| 8181 | Lakekeeper API + UI (`/ui`) | |
| 8888 | JupyterLab | |
| 8095 | `retail-api` (слой `ingestion`) | ключ `RETAIL_API_KEY` в `.env` |
| 8580 | `dbt docs serve` / SQLMesh UI в workspace | запускаются вручную: `--host 0.0.0.0 --port 8580` |
| 3070 | Dagster UI (слой `orchestration`) | 3000 на хосте занят (`secure_firefox`) |
| 8081 | Airflow UI (профиль `airflow`) | вход без пароля, только учебный стек |
| 8090 | Spark: UI менеджера кластера (`spark-master`) | |
| 4040 | Spark: UI приложения Spark Connect (jobs, stages, SQL) | gRPC 15002 — только внутри сети |
| 8084 | Redpanda Console | Kafka API 9092, Schema Registry 8081, Connect 8083 — только внутри сети |
| 8086 | Flink UI | 8081 на хосте занят Airflow |
| 8123 | ClickHouse: HTTP, веб-консоль `/play` (слой `serving`) | нативный протокол 9000 — только внутри сети |
| 8082 | Trino UI и REST API (слой `serving`) | без аутентификации, только учебный стек |
| 8088 | Superset (слой `serving`) | `admin` / `SUPERSET_ADMIN_PASSWORD` |
| 3071 | Evidence, сервер разработки (профиль `evidence`) | Vite пускает только `localhost` |
| 8080 | — | **занят на хосте** (open-webui), не использовать |
| 3000, 3001 | — | **заняты на хосте** (`secure_firefox`), не использовать |
| 8585 | OpenMetadata: UI и REST API (слой `governance`) | `admin@open-metadata.org` / `admin`; Elasticsearch 9200 — только внутри сети |

## Подключение к Iceberg из workspace

```python
from pyiceberg.catalog import load_catalog

catalog = load_catalog(
    "lakehouse", type="rest", uri="http://lakekeeper:8181/catalog", warehouse="lakehouse"
)
```

```sql
-- DuckDB (make sql)
INSTALL iceberg; LOAD iceberg; INSTALL httpfs; LOAD httpfs;
ATTACH 'lakehouse' AS lh (TYPE iceberg, ENDPOINT 'http://lakekeeper:8181/catalog', AUTHORIZATION_TYPE 'none');
SHOW ALL TABLES;
```

## Загрузка данных: dlt и эмуляторы источников (модуль 04)

- Переменные dlt заданы в окружении workspace (`core.yaml`): ключи S3 для `filesystem`
  (`DESTINATION__…`, `SOURCES__FILESYSTEM__…`), строка подключения `retail_oltp`
  (`SOURCES__SQL_DATABASE__CREDENTIALS`), ключ учебного API (`SOURCES__RETAIL_API__API_KEY`),
  REST-каталог для Iceberg (`ICEBERG_CATALOG__…`). Рабочие папки пайплайнов — `data/.dlt`
  (`DLT_DATA_DIR`), вне git.
- dlt пишет Iceberg только внутри warehouse Lakekeeper: `bucket_url="s3://warehouse/lakehouse/…"`.
- `scripts/landing_drop.py` — файлы продаж за дни в `s3://landing/freshretail/sales/dt=…/`
  (повторная доставка — повторный запуск; `--drift add|rename` — изменение схемы).
- `scripts/retail_oltp_changes.py` — изменения в `retail_oltp` (`--changes N --seed S`,
  `--slow-tx SECONDS`, `--loop SECONDS`). Схема базы — контракт лабы 04.2.
- `retail-api`: `RETAIL_API_FAIL_RATE` и `RETAIL_API_RPS` можно переопределить при запуске:
  `RETAIL_API_FAIL_RATE=0.3 make up PROFILES="ingestion"`.

## Оркестрация: Dagster и Airflow (модуль 06)

```
 браузер :3070 → dagster-webserver ─┐ gRPC :4000
                 dagster-daemon ─────┼──────────► dagster-demo (code-сервер: код и запуски,
                                     │              окружение workspace через extends)
                 Postgres, база dagster ◄── история запусков, события, тики, слоты пулов
```

- `dagster-db-init` однократно создаёт базу `dagster`: скрипты `postgres/init` выполняются только
  при первой инициализации тома.
- `dagster/dagster.yaml` — экземпляр: хранилище Postgres, `concurrency.runs` (4 запуска) и
  `concurrency.pools` (лимит 1: пул `duckdb`, один писатель файла DuckDB), логи шагов в
  `data/.dagster/`. `dagster/workspace.yaml` — code locations (gRPC-серверы).
- Новый проект = новый code-сервер (копия `dagster-demo` со своим `working_dir` и `-m`) + строка
  в `workspace.yaml`. Новый код — Deployment → Reload в UI.
- `make dagster ARGS="…"` — CLI в `dagster-demo` (для `asset …` модуль подставляется сам),
  `make dagster-shell` — оболочка.
- Airflow (`make up PROFILES="airflow"`): образ `debd/airflow:3.3.2` (`airflow/Dockerfile`,
  + DuckDB), `airflow standalone` на SQLite, DAG из `modules/06_orchestration/airflow_demo/dags`.
  Работает от `HOST_UID:0` (права на том), задачи ходят в Execution API по
  `http://localhost:8080/execution/` внутри контейнера.

## Spark (модуль 07)

```
 workspace (pyspark-client, без JVM) ──gRPC sc://spark-connect:15002──► spark-connect (driver, UI :4040)
                                                                          │ задачи
                         spark-master (UI :8090) ◄── ресурсы ──►  spark-worker-1 / -2 (executors)
                                                                          │ vended credentials
                                                         Lakekeeper (каталог lh) → Silo (S3)
```

- Образ `debd/spark:4.1.3` (`spark/Dockerfile`): официальный `apache/spark:4.1.3-…-python3-ubuntu`
  + `iceberg-spark-runtime-4.1_2.13` и `iceberg-aws-bundle` 1.12.0 + Python 3.12 для executors
  (Python UDF требуют той же версии, что у клиента) + пользователь `dev` с UID/GID хоста (Hadoop
  требует запись в `/etc/passwd`; executors пишут в смонтированный репозиторий).
- `spark/spark-defaults.conf`: каталог `lh` (REST Lakekeeper, vended credentials, S3FileIO),
  расширения Iceberg, по executor на worker (2 ядра, 2 ГБ), всего 4 ядра; AQE.
- Репозиторий смонтирован в `/workspace` у всех сервисов: executors читают
  `/workspace/data/raw/...` по тому же пути, что клиент.
- Кластер занимает ~5,5 ГБ: останавливай его, когда не нужен (команда — в README модуля 07).

## Стриминг и CDC (модуль 08)

```
 workspace (confluent-kafka) ─► redpanda:9092 (Kafka API) ◄─ connect:8083 (Debezium) ◄─ Postgres WAL
                                  │  Schema Registry :8081                         (wal_level=logical)
 Console :8084 ───────────────────┤
 flink-jobmanager (UI :8086) ─────┴─► flink-taskmanager ─► Iceberg (Lakekeeper, vended credentials)
```

- Postgres запускается с `-c wal_level=logical` (`core.yaml`) — для логической репликации Debezium.
  После пересоздания Postgres у Lakekeeper на несколько секунд ломается пул соединений, и
  `lakekeeper-init` может упасть с кодом 22 — повтори `make up`.
- Kafka Connect: секреты коннекторов — `${env:POSTGRES_PASSWORD}` (`EnvVarConfigProvider`).
  Офсеты коннектора переживают его удаление: перед пересозданием с тем же именем —
  `PUT …/stop` и `DELETE …/offsets`.
- Flink: образ `debd/flink:2.1.3` (`flink/Dockerfile`) — Kafka 5.0.0-2.1, Avro Confluent, Iceberg
  1.12 runtime + AWS bundle, Hadoop client 3.4.3. Чекпоинты каждые 10 с в общем томе
  `flink-checkpoints`. SQL — `make flink-sql ARGS="-f /workspace/…sql"`; формат `debezium-json`
  требует `REPLICA IDENTITY FULL` у таблиц-источников.
- `make rpk ARGS="…"` — CLI Redpanda (`make -s`, если вывод идёт дальше по конвейеру).

## Отдача и BI (модуль 10)

```
 Iceberg (Lakekeeper + Silo) ──DataLakeCatalog──► clickhouse:8123 (MergeTree, витрины дашборда)
        │                                              │
        └──── каталоги iceberg / postgresql / clickhouse ──► trino:8080 (UI :8082)
                                                       │
 superset:8088 ◄── clickhousedb:// · trino:// ─────────┘        evidence:3071 ◄── Trino (sources)
 (метаданные — база superset в Postgres)                         make report → build/
```

- **ClickHouse** `26.8.15.10`: пользователь и пароль — `CLICKHOUSE_USER`/`CLICKHOUSE_PASSWORD`.
  Репозиторий смонтирован только на чтение в `/workspace`: `make ch ARGS="--queries-file
  modules/…sql"`; `user_files_path` = `/workspace/data`, поэтому `file('raw/…/*.parquet')`.
  `CLICKHOUSE_DO_NOT_CHOWN=1` обязателен: иначе entrypoint делает `chown -R` папки `user_files_path`.
  Память сервера — до 4 ГБ (`clickhouse/config.d/serving.xml`). Iceberg: `SET
  allow_database_iceberg = 1` + `DataLakeCatalog` (beta), ключи S3 — от Lakekeeper.
- **Trino** `483`: каталоги — `trino/catalog/*.properties`, секреты через `${ENV:…}`, Iceberg с
  vended credentials. `mem_limit: 3g`, куча — 80 % лимита. CLI — `make trino`.
- **Superset** `6.1.0`: свой образ `debd/superset:6.1.0` (`superset/Dockerfile`: psycopg2-binary,
  clickhouse-connect, trino). `superset-db-init` создаёт базу `superset`, `superset-init` —
  миграции и админа. Кэш — SimpleCache 600 с. `SUPERSET_SECRET_KEY` шифрует пароли подключений:
  не меняй его после первого запуска.
- **Evidence** — открытый фреймворк `@evidence-dev/evidence` 40.1.8 на `node:22.20.0-slim`; проект —
  `EVIDENCE_DIR` (по умолчанию учебный отчёт), зависимости — в его `node_modules` (вне git), кэш
  npm — `data/.npm`. При старте: `npm ci`, `npm run sources`, `npm run dev`. Сборка сайта —
  `make report` (останавливает сервер разработки: они делят папку `.evidence`). Телеметрия
  выключена (`SEND_ANONYMOUS_USAGE_STATS=no`).
- Python-клиенты в workspace (группа `serving`): `clickhouse-connect`, `trino`, `dbt-metricflow`.

## Governance (модуль 11)

```
 om-ingest (CLI metadata + YAML в git) ──REST, токен бота──► openmetadata:8585 ◄── spark-lineage
   читает Trino, Postgres, dbt (target/), Superset              │      (spark-submit local[2]
                                                                 │       + агент OpenLineage)
                            Postgres, база openmetadata ◄────────┴────► elasticsearch (поиск, граф)
```

- **OpenMetadata** `2.0.3` на общем Postgres 17 (база `openmetadata`, создаёт `om-db-init`;
  миграции — `om-migrate`) и Elasticsearch `9.3.0` (1 ГБ кучи). Встроенный Airflow не ставится
  (`PIPELINE_SERVICE_CLIENT_ENABLED=false`): сбор метаданных — `make om-ingest CFG=…yaml` в
  разовом контейнере `openmetadata/ingestion:2.0.3`; переменные `${…}` в YAML подставляются из
  окружения. `OM_FERNET_KEY` шифрует пароли подключений.
- `make om-token` — токен бота `ingestion-bot` в `.env` (`OM_INGESTION_TOKEN`) и сервис пайплайнов
  `openlineage`, к которому OpenMetadata привязывает события OpenLineage.
- **spark-lineage** — образ `debd/spark:4.1.3` (в нём `openlineage-spark` 1.53.0) в локальном
  режиме; `spark/submit_with_lineage.sh` шлёт события составным транспортом: HTTP в
  `/api/v1/openlineage/lineage` и файл `data/openlineage/events.jsonl`. Кластер модуля 07 не нужен.
- **Trino**: правила доступа `trino/rules.json` (перечитываются каждые 10 с). Последнее правило
  даёт полный доступ всем прочим пользователям — Superset, Evidence и dbt работают как раньше.

## DataOps (модуль 12)

- **pre-commit** — в образе workspace (группа `dev`): `make precommit [ARGS="--all-files"]`;
  git-хук `scripts/git-hooks/pre-commit` → `make precommit`, ставится `make hooks` (нужен `.git` в
  корне курса). Кэш хуков — `data/.pre-commit`.
- **CI** — `.github/workflows/ci.yml` (для отдельного репозитория курса), шаги `scripts/ci/*.sh`.
  Локально — `make ci [CI_STEPS="lint test dbt"]` в чистом контейнере `ghcr.io/astral-sh/uv:python3.12-bookworm-slim`
  без стека: venv — `data/.ci-venv`, кэш — `data/.uv-cache`, состояние slim CI — `data/ci_state`.
- **Terraform** — `hashicorp/terraform:1.16.5` в контейнере: `make tf ARGS="plan" [TF_DIR=…]`;
  ключи S3 и Postgres — из `.env`; state — бакет `tfstate` в Silo (создаёт `silo-init`),
  блокировка `use_lockfile`. Кэш провайдеров — `data/.terraform/<папка>`.

## Частые операции

| Задача | Команда |
|---|---|
| Статус / логи | `make ps`, `make logs S=lakekeeper` |
| Добавить Python-пакет | `make uv ARGS="add --group spark pyspark"` → `make build` → `make up` |
| Dagster CLI / оболочка (модуль 06) | `make dagster ARGS="asset list"`, `make dagster-shell` |
| Redpanda CLI (модуль 08) | `make rpk ARGS="topic list"` |
| Flink SQL (модуль 08) | `make flink-sql ARGS="-f /workspace/…sql"` |
| ClickHouse / Trino (модуль 10) | `make ch`, `make trino` |
| OpenMetadata (модуль 11) | `make om-token`, `make om-ingest CFG=…`, `make spark-lineage` |
| pre-commit / CI / Terraform (модуль 12) | `make precommit`, `make ci`, `make tf ARGS="plan"` |
| Собрать отчёт Evidence (модуль 10) | `make report` (свой проект — `EVIDENCE_DIR=… make report`) |
| Видео-объяснение | `make video SCENE=modules/…/<тема>_video.py [Q=l] [VOICE=piper]` → `<тема>.mp4` рядом (по умолчанию ElevenLabs) |
| Остановить тяжёлый слой | `docker compose --env-file .env -f infra/docker/compose.yaml stop <сервисы>` |
| Остановить (данные сохраняются) | `make down` |
| Удалить всё вместе с данными | `make clean` |
| Место на диске | `docker system df`, `docker image prune` |
