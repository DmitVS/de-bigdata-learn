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
- groupBy изнутри: частичная агрегация до shuffle и финальная после
- join изнутри: sort-merge vs broadcast hash vs shuffle hash; связь с MapReduce (Клеппман, гл. 10)
- Spark SQL и DataFrame API; Spark + Iceberg (MERGE, compaction)
- тестирование трансформаций: pytest + chispa
- когда Spark не нужен: DuckDB/Polars на одной машине

## Инструменты

Apache Spark (слой `spark.yaml`), PySpark, chispa

## Лабы

Каждая лаба — папка `labs/<номер>_<название>/` с README по [шаблону](../../templates/lab_README.md).

- [ ] 07.1 — кластер Spark в compose + Iceberg через Lakekeeper
- [ ] 07.2 — трансформации через тесты (по мотивам Surfalytics #10)
- [ ] 07.3 — разбор Spark UI: предсказать план groupBy/join, проверить в UI; shuffle и skew на почасовых данных
- [ ] 07.4 — одна задача: DuckDB vs Polars vs PySpark на 116 млн и ×10 строк

## Мини-проект (вклад в capstone)

Витрина «восстановленный спрос при out-of-stock» на Spark.

## Ресурсы

- [Data-Learn: модуль 7 — Apache Spark](https://github.com/Data-Learn/data-engineering/blob/master/DE-101%20Modules/Module07/readme.md)
- [Surfalytics: Spark transformations with tests](https://github.com/surfalytics/data-projects/tree/main/de-projects/10_spark_transformations_with_tests_framework)
- [Learning Spark 2.0 (есть в репо Data-Learn)](https://github.com/Data-Learn/data-engineering/blob/master/DE-101%20Modules/Module07)

## Книга и видео

Полная таблица с пояснениями, зачем читать и что пропустить — в [карте чтения](../../reading_map.md#07--батч-обработка-spark).

- 📖 Клеппман, гл. 10 целиком — пакетная обработка и алгоритмы соединений
- 📖 Клеппман, гл. 6 — перекосы и горячие ключи
- 🎬 [Zoomcamp `06-batch`](https://github.com/DataTalksClub/data-engineering-zoomcamp/tree/main/06-batch) — особенно анатомия кластера, GroupBy и Join изнутри

## Домашка-чекпоинт

После всех лаб — `homework.md` по [шаблону](../../templates/homework.md).

## Заметки

Конспект, тезисы по книге и выводы — в [`notes.md`](notes.md).
