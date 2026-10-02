---
type: term
aliases: [Flink, Apache Flink, Flink SQL, jobmanager, taskmanager, состояние, state, sql-client]
tags: [streaming]
---

# Apache Flink

**Движок потоковой обработки: jobmanager координирует задания, taskmanager выполняет операторы в слотах. Flink SQL описывает источники и приёмники DDL с коннекторами (Kafka, Iceberg, debezium-json) и считает окна по времени события; состояние операторов (окна, changelog) сохраняется чекпоинтами.**

> [!tip] Аналогия
> Сортировочный центр, работающий непрерывно.

**У нас:** Flink 2.1.3 (`debd/flink:2.1.3`: Kafka 5.0.0-2.1, Avro Confluent, Iceberg 1.12, Hadoop client), UI <http://localhost:8086>, SQL — `make flink-sql ARGS="-f /workspace/…sql"`, чекпоинты каждые 10 с в томе `flink-checkpoints`.

Связано: [watermark](watermark.md) · [чекпоинт](checkpoint.md) · [Iceberg](iceberg.md)
