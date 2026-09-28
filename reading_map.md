# Карта чтения и видео: Клеппман и DE Zoomcamp по модулям

Два внешних источника, которые идут параллельно с курсом:

- **Мартин Клеппман, «Высоконагруженные приложения. Программирование, масштабирование,
  поддержка»** (Питер) — перевод 1-го издания *Designing Data-Intensive Applications* (DDIA).
  Даёт теорию «почему так устроено», которой нет в документации инструментов. Номера глав ниже —
  по 1-му изданию. Во 2-м издании (англ., в соавторстве с Крисом Риккомини) главы переставлены,
  поэтому ищи по названию главы (в скобках — английское название).
- **DataTalksClub Data Engineering Zoomcamp** —
  [github.com/DataTalksClub/data-engineering-zoomcamp](https://github.com/DataTalksClub/data-engineering-zoomcamp),
  бесплатный, видео на YouTube (для русской озвучки подходит Яндекс Браузер). Сквозной датасет
  там — NYC Taxi, стек облачный (GCP, BigQuery, Kestra). Смотри **концепции**, а практику делай
  в нашем стеке на FreshRetail. Папки ниже указаны по программе 2026 года.

Легенда: **◆ обязательно** (нужно для задач и DoD модуля) · **◇ по желанию** (углубление,
пригодится на собеседовании по system design).

Как работать с книгой: одна-две главы на модуль, читать **после теории модуля и до лаб**.
Итог чтения — в `notes.md` модуля: 3–5 тезисов своими словами и одна связь с нашим стеком
(«где это видно у нас»).

---

## 00 · Just enough: CLI, Git, Docker, Make

| Источник | Что | Зачем |
|---|---|---|
| ◆ Клеппман, гл. 10, первый раздел — пакетная обработка утилитами Unix (*Batch Processing with Unix Tools*) | Анализ лога через `cat \| awk \| sort \| uniq -c`, философия Unix | Пайпы — это прототип всех pipeline курса: неизменяемый вход, маленькие шаги, единый интерфейс |
| ◆ Zoomcamp [`01-docker-terraform`](https://github.com/DataTalksClub/data-engineering-zoomcamp/tree/main/01-docker-terraform) — часть Docker | Docker, Postgres в контейнере, docker compose, загрузка CSV в Postgres | Ещё один взгляд на то же, что в лабе 00.1; Terraform и GCP из этой папки пока пропусти |

## 01 · Роль DE и архитектура решения

| Источник | Что | Зачем |
|---|---|---|
| ◆ Клеппман, гл. 1 (*Reliable, Scalable, and Maintainable Applications*) | Надёжность, масштабируемость, удобство сопровождения; описание нагрузки; перцентили (p50/p95/p99) | Словарь нефункциональных требований для `capstone/architecture.md` |
| ◇ Клеппман, гл. 12, разделы об объединении данных и «разделении» БД (*Data Integration*, *Unbundling Databases*) | Системы записи vs производные данные, lambda vs kappa | Место батча и стриминга в нашей архитектуре |
| ◇ Zoomcamp — вводное видео курса и начало [`02-workflow-orchestration`](https://github.com/DataTalksClub/data-engineering-zoomcamp/tree/main/02-workflow-orchestration) (Data Lake) | Архитектура типового DE-проекта, data lake vs warehouse | Сравнить со своей схемой |

## 02 · SQL и моделирование данных

| Источник | Что | Зачем |
|---|---|---|
| ◆ Клеппман, гл. 2 (*Data Models and Query Languages*) | Реляционная vs документная модель, декларативные запросы, нормализация | Почему у нас звёздная схема, а не JSON-документы |
| ◆ Клеппман, гл. 3, раздел «OLTP или аналитика?» (*Transaction Processing or Analytics?*) и схемы для аналитики (*Stars and Snowflakes*) | OLTP vs OLAP, звезда и снежинка | Прямая теория к эссе OLTP vs OLAP |
| ◆ Zoomcamp [`04-analytics-engineering`](https://github.com/DataTalksClub/data-engineering-zoomcamp/tree/main/04-analytics-engineering) — видео про моделирование данных | Kimball: факты, измерения, архитектура DWH | Вторая подача Кимбалла перед лабой 02.3 |

## 03 · Форматы хранения и Lakehouse

| Источник | Что | Зачем |
|---|---|---|
| ◆ Клеппман, гл. 3, раздел про столбцовое хранение (*Column-Oriented Storage*) | Сжатие столбцов, bitmap-кодирование, порядок сортировки, несколько порядков сортировки | Устройство Parquet и смысл sort order в Iceberg |
| ◆ Клеппман, гл. 4 (*Encoding and Evolution*) | Обратная и прямая совместимость, JSON/Avro/Protobuf, эволюция схем | Schema evolution в Iceberg, а позже schema contracts (04) и Schema Registry (08) |
| ◇ Клеппман, гл. 6 (*Partitioning*) | Секционирование по диапазону ключа vs по хешу, перекосы и «горячие» ключи | Как выбрать партиционирование для 116 млн строк |
| ◆ Zoomcamp [`03-data-warehouse`](https://github.com/DataTalksClub/data-engineering-zoomcamp/tree/main/03-data-warehouse) | Партиционирование и кластеризация, best practices, внутреннее устройство BigQuery | Идея «платишь за прочитанные байты»: её проверяем замерами в лабе 03.4 |

## 04 · Ingestion (EL)

| Источник | Что | Зачем |
|---|---|---|
| ◆ Zoomcamp, воркшоп по dlt ([`cohorts/2026/workshops/dlt.md`](https://github.com/DataTalksClub/data-engineering-zoomcamp/blob/main/cohorts/2026/workshops/dlt.md)) | Чтение API, пагинация, нормализация вложенных JSON, инкрементальная загрузка | Лучший бесплатный материал по dlt, почти один в один с лабами 04.1–04.4 |
| ◆ Клеппман, гл. 4 — повтор разделов про совместимость | Что ломается, когда источник меняет схему | Schema contracts в dlt |
| ◇ Клеппман, гл. 7 (*Transactions*) | ACID, уровни изоляции | Как ведёт себя `retail_oltp` и почему инкремент по `updated_at` может терять строки |

## 05 · Трансформации: dbt

| Источник | Что | Зачем |
|---|---|---|
| ◆ Zoomcamp [`04-analytics-engineering`](https://github.com/DataTalksClub/data-engineering-zoomcamp/tree/main/04-analytics-engineering) целиком | dbt с DuckDB: модели, sources, тесты, документация, деплой | Самое близкое к нашему стеку: там тоже dbt + DuckDB |
| ◇ Клеппман, гл. 3 — материализованные представления и кубы (*Aggregation: Data Cubes and Materialized Views*) | Предрасчёт агрегатов и цена этого решения | Выбор materialization: view, table или incremental |

## 06 · Оркестрация

| Источник | Что | Зачем |
|---|---|---|
| ◆ Zoomcamp [`02-workflow-orchestration`](https://github.com/DataTalksClub/data-engineering-zoomcamp/tree/main/02-workflow-orchestration) | Оркестрация на Kestra: расписания, backfill, переменные | Концепции те же, что в Dagster; полезно сравнить flow-подход с asset-подходом |
| ◆ Клеппман, гл. 10, раздел о результатах пакетной обработки (*The Output of Batch Workflows*) | Неизменяемые входы, идемпотентный перезапуск, «откат» перерасчётом | Теория к идемпотентности и backfill |
| ◇ Клеппман, гл. 8 (*The Trouble with Distributed Systems*) | Ненадёжные сети, таймауты, паузы процессов | Почему ретраи обязательны и почему они опасны без идемпотентности |
| ◇ Zoomcamp [`05-data-platforms`](https://github.com/DataTalksClub/data-engineering-zoomcamp/tree/main/05-data-platforms) | Весь pipeline на одном инструменте (Bruin) | Для сравнения: «всё в одном» против нашего набора отдельных инструментов |

## 07 · Батч-обработка: Spark

| Источник | Что | Зачем |
|---|---|---|
| ◆ Клеппман, гл. 10 целиком (*Batch Processing*) | MapReduce, соединения на стороне reduce (sort-merge) и map (broadcast hash, partitioned hash), материализация промежуточного состояния, dataflow-движки | Теоретическая основа Spark: shuffle, broadcast join и skew объясняются здесь лучше всего |
| ◆ Клеппман, гл. 6 — перекосы (*Skewed Workloads and Relieving Hot Spots*) | Горячие ключи | К разбору skew в лабе 07.3 |
| ◆ Zoomcamp [`06-batch`](https://github.com/DataTalksClub/data-engineering-zoomcamp/tree/main/06-batch) | DataFrames, Spark SQL, анатомия кластера, **GroupBy и Join изнутри**, локальный кластер | Видео про GroupBy и Join — лучшее наглядное объяснение shuffle; Dataproc и GCS пропусти |

## 08 · Стриминг и CDC

| Источник | Что | Зачем |
|---|---|---|
| ◆ Клеппман, гл. 11 целиком (*Stream Processing*) | Брокеры сообщений vs логи, CDC, event sourcing, время события vs время обработки, окна, соединения потоков, отказоустойчивость | Главная теория модуля |
| ◆ Клеппман, гл. 5, раздел о журналах репликации (*Implementation of Replication Logs*) | Логическая (построчная) репликация, WAL | Как Debezium читает изменения из Postgres |
| ◇ Клеппман, гл. 9 (*Consistency and Consensus*) и гл. 12 про корректность (*Aiming for Correctness*) | Упорядочение, exactly-once, идемпотентность, end-to-end | К эссе про exactly-once |
| ◆ Zoomcamp [`07-streaming`](https://github.com/DataTalksClub/data-engineering-zoomcamp/tree/main/07-streaming) | Kafka: producer/consumer, партиции, Avro и Schema Registry, Kafka Streams, KSQL | Kafka-часть — прямо к 08.1–08.2; из Kafka Streams и KSQL бери идеи (двойственность потока и таблицы, окна), реализуем их во Flink SQL |

## 09 · Качество и наблюдаемость

| Источник | Что | Зачем |
|---|---|---|
| ◆ Клеппман, гл. 1 — повтор раздела о перцентилях | p95/p99 вместо среднего | SLO свежести формулируем через перцентиль |
| ◇ Клеппман, гл. 12 — проверка целостности (*Trust, but Verify*) | Аудит производных данных, сквозные проверки | Идея reconciliation-проверок «источник = витрина» |
| ◇ Zoomcamp [`05-data-platforms`](https://github.com/DataTalksClub/data-engineering-zoomcamp/tree/main/05-data-platforms) — часть про качество | Проверки качества внутри pipeline | Сравнить с dbt tests + Soda |

## 10 · Витрины и BI

| Источник | Что | Зачем |
|---|---|---|
| ◆ Клеппман, гл. 3 — LSM-деревья и SSTable (*SSTables and LSM-Trees*) | Запись в отсортированные сегменты и фоновое слияние | Так устроен MergeTree в ClickHouse; отсюда смысл `ORDER BY` в DDL |
| ◆ Zoomcamp [`03-data-warehouse`](https://github.com/DataTalksClub/data-engineering-zoomcamp/tree/main/03-data-warehouse) — best practices | Стоимость запроса, кластеризация | Перенести на ClickHouse: сколько строк и байт прочитал запрос |
| ◇ Zoomcamp [`04-analytics-engineering`](https://github.com/DataTalksClub/data-engineering-zoomcamp/tree/main/04-analytics-engineering) — видео про визуализацию | Дашборд поверх dbt-моделей | Минимальные требования к дашборду — см. [рубрику capstone](capstone/rubric.md) |

## 11 · Governance

| Источник | Что | Зачем |
|---|---|---|
| ◆ Клеппман, гл. 12, последний раздел (*Doing the Right Thing*) | Этика данных, приватность, слежка, ответственность инженера | Зачем маскирование и PII-политики, кроме требований закона |

## 12 · DataOps и CI/CD

| Источник | Что | Зачем |
|---|---|---|
| ◆ Zoomcamp [`01-docker-terraform`](https://github.com/DataTalksClub/data-engineering-zoomcamp/tree/main/01-docker-terraform) — часть Terraform | `init` / `plan` / `apply`, провайдер, переменные | Теперь можно смотреть то, что пропустил в модуле 00: ровно то, что нужно к лабе 12.3 |
| ◆ Клеппман, гл. 1 — удобство сопровождения (*Maintainability*) | Удобство эксплуатации, простота, способность к развитию | Язык, которым обосновываются CI, линтеры и тесты |
| ◇ Zoomcamp [`04-analytics-engineering`](https://github.com/DataTalksClub/data-engineering-zoomcamp/tree/main/04-analytics-engineering) — деплой dbt | dbt в проде, CI | Сравнить со своим slim CI |

## 13 · (опц.) Облачное хранилище

| Источник | Что | Зачем |
|---|---|---|
| ◆ Zoomcamp [`03-data-warehouse`](https://github.com/DataTalksClub/data-engineering-zoomcamp/tree/main/03-data-warehouse) | BigQuery: раздельные storage и compute, модель оплаты | Второй облачный DWH для сравнения со Snowflake |

## Capstone

| Источник | Что | Зачем |
|---|---|---|
| ◆ Zoomcamp [`projects`](https://github.com/DataTalksClub/data-engineering-zoomcamp/tree/main/projects) | Критерии оценки и peer review | Адаптировано в [`capstone/rubric.md`](capstone/rubric.md) |
| ◇ Клеппман, гл. 5, 7, 9 | Репликация, транзакции, консенсус | Подготовка к system design на собеседованиях |

---

## Что сознательно не берём из Zoomcamp

- **GCP, BigQuery, Dataproc, GCS** как рабочую среду: у нас только локальный Docker, облако —
  лишь в опциональном модуле 13 и в Terraform-обзоре (plan без apply).
- **Kestra**: оркестратор курса — Dagster; видео смотрим ради концепций.
- **Kafka Streams и KSQL** как инструменты: они на JVM-стеке Confluent, у нас Flink SQL.
- **Датасет NYC Taxi**: наш сквозной датасет — FreshRetail.
