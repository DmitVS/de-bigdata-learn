---
name: course-methodology
description: Методика курса — что взято из Data-Learn DE-101 и Surfalytics, что сознательно пропущено
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
