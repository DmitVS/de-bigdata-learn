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
