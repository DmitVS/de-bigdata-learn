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
