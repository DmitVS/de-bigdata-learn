---
name: course-methodology
description: Методика курса — что взято из Data-Learn DE-101, Surfalytics, DE Zoomcamp и Клеппмана, что сознательно пропущено
metadata:
  type: decision
---

Решение от 2026-09-23, по итогам разбора github.com/Data-Learn/data-engineering и surfalytics.com
(+ github.com/surfalytics/data-projects).

Взято:
- **Data-Learn:** репозиторий как учебник и портфолио; бизнес-вопрос прежде инструмента;
  финальный проект в каждом модуле; значки → чек-листы DoD в ROADMAP; советы выпускника
  (одна роль, раньше на собеседования, применять знания, публиковать); реальные take-home.
- **Surfalytics:** шаблон проекта `Objective → Key Terms → Prerequisites → Tasks + Definition of Done`;
  Module 0 «just enough» (CLI/Git/Docker); одна задача на SQL и PySpark; PyArrow, Iceberg,
  SQLMesh, Elementary, Soda, Trino, chispa; структура стриминга (Kafka core → Schema Registry →
  Connect → Debezium → Flink); DataOps (pre-commit, CI, SLA/SLO/SLI, MTTD/MTTR, DORA);
  mock-интервью по сценарию; трёхфазная каденция (фундамент → портфолио → работа) с еженедельными отчётами.

Пропущено: Pentaho, Tableau Prep, Alteryx, Azure Synapse, Redshift, Fabric, Looker (устарели
или привязаны к вендору); Hadoop — только теория; Snowflake — опциональный модуль 13.

Отложено до конца курса (явное решение пользователя): LLM в работе инженера данных
(Claude Code для data-задач, surfalytics/ClaudeCode101).

## Дополнение от 2026-09-27: DE Zoomcamp и Клеппман

Взято:
- **DataTalksClub DE Zoomcamp:** домашка-чекпоинт в конце модуля (вопросы с однозначным ответом,
  получаемым запросом — `templates/homework.md`); рубрика финального проекта и peer review →
  `capstone/rubric.md` (облако заменено на IaC, добавлены качество, стриминг, документация);
  партиционирование + кластеризация и «стоимость = прочитанные байты» (модули 03, 10);
  GroupBy/Join изнутри (07); требование к дашборду «категории + динамика» (10); воркшоп по dlt (04).
- **Клеппман, «Высоконагруженные приложения»:** главы к каждому модулю, тезисы в `notes.md`;
  темы NFR и перцентилей (01, 09), OLTP/OLAP и столбцовое хранение (02, 03), эволюция схем
  (03, 04, 08), алгоритмы соединений (07), лог vs брокер, CDC через WAL, время события (08),
  LSM → MergeTree (10), этика данных (11).
- Карта «модуль → главы → видео» — `reading_map.md`.

Не взято из Zoomcamp: GCP/BigQuery/Dataproc как рабочая среда, Kestra, Kafka Streams/KSQL, NYC Taxi.
