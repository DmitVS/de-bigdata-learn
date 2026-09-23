# Модуль 07 · Батч-обработка: Apache Spark

**Длительность:** ~2 нед. · **Статус и DoD:** см. [ROADMAP](../../ROADMAP.md)

## Бизнес-вопрос

> Когда данных становится слишком много для одной машины — как распределить обработку?

## Цели

- понимать модель выполнения Spark
- читать Spark UI и лечить shuffle/skew
- писать тестируемые трансформации

## Темы

- driver/executors, jobs/stages/tasks, lazy evaluation
- партиционирование, shuffle, skew, broadcast join, AQE
- Spark SQL и DataFrame API; Spark + Iceberg (MERGE, compaction)
- тестирование трансформаций: pytest + chispa
- когда Spark не нужен: DuckDB/Polars на одной машине

## Инструменты

Apache Spark (слой `spark.yaml`), PySpark, chispa

## Лабы

Каждая лаба — папка `labs/<номер>_<название>/` с README по [шаблону](../../templates/lab_README.md).

- [ ] 07.1 — кластер Spark в compose + Iceberg через Lakekeeper
- [ ] 07.2 — трансформации через тесты (по мотивам Surfalytics #10)
- [ ] 07.3 — разбор Spark UI: shuffle и skew на почасовых данных
- [ ] 07.4 — одна задача: DuckDB vs Polars vs PySpark на 116 млн и ×10 строк

## Мини-проект (вклад в capstone)

Витрина «восстановленный спрос при out-of-stock» на Spark.

## Ресурсы

- [Data-Learn: модуль 7 — Apache Spark](https://github.com/Data-Learn/data-engineering/blob/master/DE-101%20Modules/Module07/readme.md)
- [Surfalytics: Spark transformations with tests](https://github.com/surfalytics/data-projects/tree/main/de-projects/10_spark_transformations_with_tests_framework)
- [Learning Spark 2.0 (есть в репо Data-Learn)](https://github.com/Data-Learn/data-engineering/blob/master/DE-101%20Modules/Module07)

## Заметки

Конспект и выводы — в [`notes.md`](notes.md).
