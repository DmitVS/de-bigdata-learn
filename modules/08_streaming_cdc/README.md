# Модуль 08 · Стриминг и CDC

**Длительность:** ~2 нед. · **Статус и DoD:** см. [ROADMAP](../../ROADMAP.md)

## Бизнес-вопрос

> Как видеть продажи и out-of-stock почти в реальном времени и не терять изменения в учётной системе?

## Цели

- понимать модель Kafka
- построить CDC из Postgres
- считать оконные агрегаты во Flink

## Темы

- брокер сообщений vs лог (Клеппман, гл. 11); двойственность потока и таблицы
- Kafka: топики, партиции, offsets, consumer groups, retention, compaction
- Schema Registry: Avro/Protobuf, совместимость схем
- Kafka Connect, Debezium CDC; логическая репликация и WAL Postgres как основа CDC
- время события vs время обработки
- Flink SQL: окна, watermarks, late data, exactly-once, state
- стриминг в lakehouse: Iceberg sink

## Инструменты

Redpanda + Console, Schema Registry, Kafka Connect/Debezium, Flink (слой `streaming.yaml`)

## Лабы

Каждая лаба — папка `labs/<номер>_<название>/` с README по [шаблону](../../templates/lab_README.md).

- [ ] 08.1 — Redpanda: produce/consume, партиции, consumer groups
- [ ] 08.2 — producer: «проигрывание» почасовых продаж как событий
- [ ] 08.3 — Debezium: CDC `retail_oltp` → Kafka → Iceberg
- [ ] 08.4 — Flink SQL: продажи и out-of-stock по магазину/часу

## Мини-проект (вклад в capstone)

Потоковая витрина out-of-stock + SCD2 справочников из CDC.

## Ресурсы

- [Surfalytics: Data Streaming Mastery](https://github.com/surfalytics/data-projects/tree/main/async-projects/data-streaming-mastery)
- [Designing Data-Intensive Applications (Kleppmann) — гл. 11](https://dataintensive.net/)

## Книга и видео

Полная таблица с пояснениями, зачем читать и что пропустить — в [карте чтения](../../reading_map.md#08--стриминг-и-cdc).

- 📖 Клеппман, гл. 11 целиком — потоковая обработка
- 📖 Клеппман, гл. 5 — журналы репликации (основа CDC)
- 🎬 [Zoomcamp `07-streaming`](https://github.com/DataTalksClub/data-engineering-zoomcamp/tree/main/07-streaming) — Kafka, Avro и Schema Registry; Kafka Streams — ради идей

## Домашка-чекпоинт

После всех лаб — `homework.md` по [шаблону](../../templates/homework.md).

## Заметки

Конспект, тезисы по книге и выводы — в [`notes.md`](notes.md).
