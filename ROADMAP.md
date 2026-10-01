# ROADMAP — Data Engineering на Modern Data Stack

Один сквозной проект вместо разрозненных туториалов: каждый модуль добавляет слой к pipeline
над датасетом **FreshRetailNet-50K** (сеть Dingdong: 898 магазинов, 863 SKU, почасовые продажи,
остатки, промо, погода). Всё работает локально в Docker Compose.

**Принципы** (взяты из [Data-Learn DE-101](https://github.com/Data-Learn/data-engineering),
[Surfalytics](https://github.com/surfalytics/data-projects),
[DE Zoomcamp](https://github.com/DataTalksClub/data-engineering-zoomcamp) и книги Клеппмана, подробнее — [`memory/decisions/course-methodology.md`](memory/decisions/course-methodology.md)):

1. **Сначала бизнес-вопрос, потом инструмент.** Каждый модуль начинается с вопроса к данным сети.
2. **Репозиторий — учебник и портфолио.** Каждая лаба — папка с README по
   [шаблону](templates/lab_README.md) (`Objective → Key Terms → Prerequisites → Tasks + Definition of Done`)
   и результатом, закоммиченным в git.
3. **Модуль закрыт, только когда выполнен его чек-лист DoD** (аналог значков DE-101).
4. **Одна задача — несколько движков**: SQL (DuckDB) / Polars / PySpark, где это имеет смысл.
5. **Мини-проект в конце модуля** наращивает [capstone](capstone/README.md).
6. **Еженедельное ретро** в [`plans/weekly/`](plans/weekly/) и **публикация** по итогам модуля в [`blog/`](blog/).
7. **Собеседования начинаются рано**: с фазы 2 — take-home и mock-интервью из [`interview/`](interview/).
8. **Домашка-чекпоинт в конце модуля** (из Zoomcamp): 5–7 вопросов с однозначным ответом,
   который получается запросом к нашему стеку — [шаблон](templates/homework.md).
9. **Книга и видео параллельно**: к каждому модулю — главы Клеппмана и разделы Zoomcamp по
   [карте чтения](reading_map.md); 3–5 тезисов своими словами — в `notes.md` модуля.
10. **Capstone оценивается по рубрике** и проходит peer review — [`capstone/rubric.md`](capstone/rubric.md).

Отметка `[x]` ставится, когда выполнен пункт DoD. Статус модуля: ⬜ не начат · 🟨 в работе · ✅ закрыт.

---

## Фаза 1 — Фундамент (недели 1–6)

### 🟨 00 · Just enough: CLI, Git, Docker, Make — [модуль](modules/00_just_enough/README.md)
- [x] `make up` поднимает core, `make check` — все проверки OK
- [ ] Разобран каждый сервис в `infra/docker/core.yaml`: что делает, порты, тома, healthcheck
- [ ] Датасет скачан (`make data`); расхождения фактической статистики с описанием (863 vs 865 SKU, период) объяснены
- [ ] Шпаргалка [`cheatsheet.md`](modules/00_just_enough/README.md) модуля своими словами

### ⬜ 01 · Роль DE и архитектура решения — [модуль](modules/01_role_and_architecture/README.md)
- [ ] 5–10 бизнес-вопросов сети к данным зафиксированы в `capstone/README.md`
- [ ] Схема целевой архитектуры (Mermaid) в `capstone/architecture.md`
- [ ] Обзор 10 вакансий DE (hh.ru / LinkedIn): частотность навыков → `interview/market.md`

### ⬜ 02 · SQL и моделирование данных — [модуль](modules/02_sql_and_modeling/README.md)
- [ ] Лабы по оконным функциям, CTE, `QUALIFY`, `UNNEST` на FreshRetail в DuckDB
- [ ] Звёздная схема (Kimball): факты продаж/остатков, измерения store/product/date → ER-диаграмма
- [ ] Эссе: OLTP vs OLAP, Kimball vs Data Vault vs One Big Table, SCD 0/1/2
- [ ] Мини-проект: SQL-ответы на 3 бизнес-вопроса из модуля 01

### ⬜ 03 · Форматы хранения и Lakehouse — [модуль](modules/03_storage_and_lakehouse/README.md)
- [ ] PyArrow: схема, row groups, статистики Parquet; сравнение CSV/Parquet/сжатий
- [ ] Iceberg: таблица bronze в Lakekeeper, snapshots, time travel, schema evolution, hidden partitioning
- [ ] Разворот почасовых массивов → ~116 млн строк; партиционирование и замер скорости запросов
- [ ] Порядок сортировки (sort order) в Iceberg: замер прочитанных файлов и байт с ним и без него
- [ ] Мини-проект: bronze-слой FreshRetail в Iceberg, читается из DuckDB

### ⬜ 04 · Ingestion (EL) — [модуль](modules/04_ingestion/README.md)
- [ ] dlt: загрузка файлов из S3 `landing` → Iceberg, инкрементальность, повторная доставка без дублей, schema contracts
- [ ] Справочники сети загружены в Postgres `retail_oltp` (эмуляция учётной системы); изменения генератора найдены запросами
- [ ] dlt: Postgres → lakehouse (full vs incremental): что теряет каждый вариант — сверкой; триггер и окно перечитывания
- [ ] dlt: учебный API (пагинация, 429/503) и публичный API праздников → lakehouse; расхождения с `holiday_flag` объяснены
- [ ] Одна трансформация в трёх вариантах: SQL / Polars / pandas — замер и выводы
- [ ] Мини-проект: три источника в bronze одной командой `make ingest`, повтор без дублей

### ⬜ 05 · Трансформации: dbt — [модуль](modules/05_transformation_dbt/README.md)
- [ ] dbt-проект `capstone/transform`: staging → intermediate → marts, sources, refs
- [ ] Тесты (generic, singular, unit tests), документация, `dbt docs`
- [ ] Документация и lineage в dbt: описания в YAML, docs blocks, `persist_docs`; анализ влияния через `dbt ls --select +модель+`
- [ ] Проверка: у каждой модели слоя marts есть описание (падает, если нет)
- [ ] Инкрементальные модели (окно перечитывания), snapshots (SCD2 по справочникам retail_oltp), макросы, пакеты
- [ ] Витрины опубликованы в Iceberg `gold` и читаются из чистого DuckDB
- [ ] Сравнение: та же модель на SQLMesh — плюсы/минусы
- [ ] Мини-проект: витрины «продажи», «out-of-stock», «эффект промо»

## Фаза 2 — Масштаб и портфолио (недели 7–13)

### ⬜ 06 · Оркестрация — [модуль](modules/06_orchestration/README.md)
- [ ] Dagster в compose: assets для dlt + dbt, расписания, сенсоры, партиции, backfill
- [ ] Граф ассетов от загрузки до витрин в UI Dagster; по графу разобрано, что пересчитать после сбоя одного ассета
- [ ] (опц.) Тот же pipeline на Airflow 3 — сравнение подходов asset vs task
- [ ] Мини-проект: весь pipeline 03–05 запускается одной кнопкой / по расписанию

### ⬜ 07 · Батч-обработка: Spark — [модуль](modules/07_batch_spark/README.md)
- [ ] Spark-кластер в compose + Iceberg; чтение/запись через Lakekeeper
- [ ] Партиционирование, shuffle, skew, broadcast join, AQE — разбор Spark UI
- [ ] GroupBy и join изнутри: двухфазная агрегация, sort-merge vs broadcast hash join — предсказать план, проверить в UI
- [ ] Трансформации через тесты: pytest + chispa
- [ ] Одна задача: DuckDB vs Polars vs PySpark на 116 млн строк (и ×10 синтетике) — выводы
- [ ] Мини-проект: тяжёлая витрина (восстановление спроса при out-of-stock) на Spark

### ⬜ 08 · Стриминг и CDC — [модуль](modules/08_streaming_cdc/README.md)
- [ ] Redpanda: топики, партиции, consumer groups; Schema Registry (Avro/Protobuf)
- [ ] Kafka Connect + Debezium: CDC из `retail_oltp` → Kafka → Iceberg
- [ ] Producer «проигрывает» почасовые продажи как поток событий
- [ ] Flink SQL: оконные агрегаты (продажи и out-of-stock по магазину/часу) → Iceberg/ClickHouse
- [ ] Эссе: exactly-once, watermarks, late data

### ⬜ 09 · Качество и наблюдаемость данных — [модуль](modules/09_quality_observability/README.md)
- [ ] dbt tests + Soda checks на ключевых таблицах; data contracts
- [ ] Elementary: отчёт и алерты по прогонам dbt
- [ ] SLO pipeline (свежесть, успешность) в [`ops/slo.md`](ops/slo.md); первый разбор в [`ops/incidents.md`](ops/incidents.md)
- [ ] В разборе инцидента источник плохих данных найден по lineage (вверх по графу от витрины)

### ⬜ 10 · Витрины и BI — [модуль](modules/10_serving_bi/README.md)
- [ ] ClickHouse: витрины, MergeTree, materialized views
- [ ] Trino: федеративные запросы Iceberg + Postgres + ClickHouse
- [ ] Superset: дашборд сети (продажи, out-of-stock, промо, погода) — минимум график по категориям и график динамики во времени
- [ ] Семантический слой: метрики в одном месте
- [ ] Отчёт-страница «код + текст» (Evidence): markdown с SQL-запросами и графиками, собирается в статический сайт

## Фаза 3 — Production и карьера (недели 14–18)

### ⬜ 11 · Governance — [модуль](modules/11_governance/README.md)
- [ ] Теория lineage: таблица vs колонка, статический vs рантайм, анализ влияния и поиск причины; стандарт OpenLineage
- [ ] OpenMetadata: каталог, lineage из dbt/Dagster, владельцы, glossary
- [ ] Lineage из Spark через OpenLineage в OpenMetadata: граф от источника через Spark и dbt до дашборда
- [ ] Доступы: роли и маскирование в Trino/Postgres

### ⬜ 12 · DataOps и CI/CD — [модуль](modules/12_dataops_cicd/README.md)
- [ ] pre-commit + GitHub Actions: ruff, sqlfmt, yamllint, `dbt build` на выборке (slim CI)
- [ ] `dbt docs generate` в CI и публикация на GitHub Pages: документация обновляется при каждом изменении
- [ ] Terraform (обзор): как этот стек выглядел бы в облаке
- [ ] DORA, SLA/SLO/SLI, MTTD/MTTR — применено к своему pipeline

### ⬜ 13 · (опц.) Облачное хранилище — [модуль](modules/13_cloud_dwh_optional/README.md)
- [ ] Snowflake trial: перенос dbt-проекта, сравнение с локальным lakehouse

### ⬜ Capstone и карьера — [capstone](capstone/README.md) · [interview](interview/README.md)
- [ ] Capstone: README с архитектурой, запуск одной командой, скриншоты дашбордов
- [ ] Самооценка по [рубрике](capstone/rubric.md) ≥ 32/40 без нулей; ревью 3 чужих проектов и 1 внешнее ревью своего
- [ ] 3 take-home задания и 3 mock-интервью (SQL, моделирование, system design)
- [ ] 3+ публикации по итогам модулей
- [ ] Резюме и профиль LinkedIn отражают проект

---

## После курса

- **LLM в работе инженера данных** (Claude Code для data-задач, материалы вроде
  [surfalytics/ClaudeCode101](https://github.com/surfalytics/ClaudeCode101)) — **намеренно
  отложено** до завершения курса.
- Hadoop — только час теории для понимания истории (HDFS, MapReduce, YARN).
