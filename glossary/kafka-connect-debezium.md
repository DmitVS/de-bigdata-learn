---
type: term
aliases: [Kafka Connect, Debezium, коннектор, connector, слот репликации, публикация, REPLICA IDENTITY, op, before, after]
tags: [streaming, cdc]
---

# Kafka Connect и Debezium

**Kafka Connect — сервис, запускающий готовые коннекторы «система ↔ Kafka» по JSON-конфигу через REST API, с офсетами и статусом в служебных топиках. Debezium — коннектор-источник CDC: создаёт в Postgres публикацию и слот логической репликации, делает начальный снапшот (`op=r`) и выдаёт каждое изменение строки (`c`, `u`, `d` с `before`/`after`/`source`), после удаления — tombstone.**

> [!tip] Аналогия
> Перегрузчик, читающий бортовой журнал базы.

**У нас:** `quay.io/debezium/connect:3.7.0.Final`, REST `http://connect:8083`; секреты — `${env:POSTGRES_PASSWORD}` через `EnvVarConfigProvider`; песочница — `modules/08_streaming_cdc/demo/connect/`. Брошенный слот копит WAL — следить за `pg_replication_slots`. Офсеты коннектора переживают его удаление (`DELETE /connectors/<имя>/offsets`); Flink `debezium-json` требует `REPLICA IDENTITY FULL`.

Связано: [CDC](cdc.md) · [Kafka](kafka.md)
