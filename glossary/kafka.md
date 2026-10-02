---
type: term
aliases: [Kafka, Redpanda, топик, topic, брокер, лог событий, retention, compaction, rpk]
tags: [streaming]
---

# Kafka (Redpanda)

**Распределённый лог событий: топики из партиций, в которые события только дописываются и хранятся по политике — удалять по возрасту/размеру (retention) или оставлять последнее значение каждого ключа (compaction, `null` — tombstone). Читатели сами помнят позицию (офсет), поэтому чтение не меняет лог, а историю можно переиграть.**

> [!tip] Аналогия
> Журнал на проходной: дописывают в конец, каждый читатель держит свою закладку.

**У нас:** Redpanda v26.2 (Kafka API `redpanda:9092`, Schema Registry `:8081`), Console — <http://localhost:8084>, CLI — `make rpk ARGS="…"`. Слой `streaming.yaml`, профиль `streaming`.

Связано: [партиция Kafka](kafka-partition.md) · [офсет и группа](consumer-group.md) · [CDC](cdc.md)
