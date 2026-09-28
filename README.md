# DE BigData Learn

Самообучение Data Engineering на Modern Data Stack. Один сквозной проект над данными
розничной сети **FreshRetailNet-50K** (898 магазинов · 863 SKU · почасовые продажи, остатки,
промо, погода) — от сырых файлов до дашборда, стриминга и CI/CD.

- План курса и прогресс — [ROADMAP.md](ROADMAP.md)
- Инфраструктура — [infra/README.md](infra/README.md)
- Датасет — [datasets/README.md](datasets/README.md)
- Сквозной проект — [capstone/README.md](capstone/README.md)

## Стек

Всё работает **только в контейнерах** (Docker Compose). На хосте нужны лишь `docker` и `make`.

| Слой | Инструменты | Модуль |
|---|---|---|
| Хранилище | Silo (S3, форк MinIO), Apache Iceberg, Lakekeeper (REST-каталог) | 03 |
| OLTP-источник | Postgres (`retail_oltp`) | 04, 08 |
| Ingestion | dlt | 04 |
| Обработка | DuckDB, Polars, PyArrow, Apache Spark | 02–07 |
| Трансформации | dbt-core (+ SQLMesh для сравнения) | 05 |
| Оркестрация | Dagster (+ Airflow для сравнения) | 06 |
| Стриминг / CDC | Redpanda, Schema Registry, Kafka Connect + Debezium, Flink | 08 |
| Качество | dbt tests, Soda, Elementary | 09 |
| Витрины / BI | ClickHouse, Trino, Superset | 10 |
| Governance | OpenMetadata | 11 |
| DataOps | GitHub Actions, pre-commit, Terraform (обзор) | 12 |

## Быстрый старт

```bash
make init    # .env из шаблона
make build   # образ workspace (Python 3.12, dbt, dlt, DuckDB, Polars, PyIceberg, Jupyter)
make up      # слой core: Postgres, Silo, Lakekeeper, workspace
make check   # smoke-тест: S3, Postgres, Iceberg-каталог, DuckDB
make data    # скачать FreshRetailNet-50K в data/raw
make help    # все команды
```

| Сервис | Адрес |
|---|---|
| JupyterLab | http://localhost:8888 |
| Silo — консоль S3 | http://localhost:9001 (логин/пароль — `S3_*` из `.env`) |
| Lakekeeper UI | http://localhost:8181/ui |
| Postgres | `localhost:5432` (`POSTGRES_*` из `.env`) |

## Структура

```
├── AGENTS.md / CLAUDE.md   инструкции для AI-ассистентов
├── ROADMAP.md              план курса, чек-листы DoD по модулям
├── Makefile                единая точка входа
├── pyproject.toml, uv.lock зависимости контейнера workspace
├── infra/docker/           compose.yaml (+ слои), Dockerfile workspace, init-скрипты
├── glossary/               словарь терминов (общий на весь курс, всплывает в Obsidian)
├── reading_map.md          карта чтения: Клеппман и DE Zoomcamp по модулям
├── modules/NN_*/           цели модуля (README), labs/, notes.md
├── capstone/               сквозной проект: ingestion, transform, orchestration, streaming, quality, serving
├── datasets/               скрипты скачивания (сами данные — в data/, вне git)
├── scripts/                служебные скрипты (smoke-тест)
├── notebooks/              эксперименты
├── interview/              рынок, take-home, mock-интервью
├── ops/                    SLO, журнал инцидентов
├── blog/                   черновики публикаций
├── plans/                  планы (active/completed) и еженедельные ретро (weekly/)
├── memory/                 решения и выводы проекта
└── templates/              шаблоны лабы, плана, ретро
```

## Источники методики

- [Data-Learn DE-101](https://github.com/Data-Learn/data-engineering) — репозиторий как учебник и портфолио, бизнес-вопрос прежде инструмента
- [Surfalytics data-projects](https://github.com/surfalytics/data-projects) — формат проектов с Definition of Done, современные инструменты, DataOps
