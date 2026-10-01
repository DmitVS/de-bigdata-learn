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
| `orchestration.yaml` | Dagster (webserver + daemon), Airflow (опц.) | 1,5–4,5 ГБ | 06 | ⬜ |
| `spark.yaml` | Spark master + 2 workers | 4–6 ГБ | 07 | ⬜ |
| `streaming.yaml` | Redpanda + Console, Schema Registry, Kafka Connect/Debezium, Flink | 3–4 ГБ | 08 | ⬜ |
| `serving.yaml` | ClickHouse, Trino, Superset | 4–5 ГБ | 10 | ⬜ |
| `governance.yaml` | OpenMetadata + Elasticsearch | 5–6 ГБ | 11 | ⬜ |

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
| 8080 | — | **занят на хосте** (open-webui), не использовать |
| зарезервировано | 3000 Dagster · 8081 Airflow · 4040/8090 Spark · 19092/8084 Redpanda · 8123 ClickHouse · 8082 Trino · 8088 Superset · 3001 Evidence · 8585 OpenMetadata | для будущих слоёв |

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

## Частые операции

| Задача | Команда |
|---|---|
| Статус / логи | `make ps`, `make logs S=lakekeeper` |
| Добавить Python-пакет | `make uv ARGS="add --group spark pyspark"` → `make build` → `make up` |
| Остановить (данные сохраняются) | `make down` |
| Удалить всё вместе с данными | `make clean` |
| Место на диске | `docker system df`, `docker image prune` |
