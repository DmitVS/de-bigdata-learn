---
type: term
aliases: [чекпоинт, checkpoint, барьер, savepoint, двухфазный коммит, two-phase commit]
tags: [streaming]
---

# Чекпоинт

**Согласованный снимок офсетов источников и состояния всех операторов, который Flink делает по барьерам, идущим вместе с событиями. При сбое задание восстанавливается с последнего чекпоинта и перечитывает события. Транзакционный приёмник (Iceberg) коммитит данные только после успешного чекпоинта — так получается exactly-once до приёмника.**

> [!tip] Аналогия
> Фотография всех ящиков и закладок сразу; на склад сдают только вместе с фотографией.

**У нас:** `execution.checkpointing.interval: 10s`, `state.checkpoints.dir` — том `flink-checkpoints`, общий для jobmanager и taskmanager. Плановая остановка — stop with savepoint.

Связано: [гарантии доставки](delivery-semantics.md) · [Flink](flink.md)
