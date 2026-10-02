---
type: term
aliases: [партиция ассета, partition, DailyPartitionsDefinition, partition_key, backfill policy, политика backfill]
tags: [orchestration]
---

# Партиции ассета

**Разбиение ассета на независимо материализуемые части с ключами (обычно дни). Статус хранится по каждой партиции; шаг получает ключ в `context.partition_key` и заменяет ровно эту часть данных. Политика backfill задаёт, сколько партиций обрабатывает один запуск.** Партиция — единица идемпотентности и перезапуска.

> [!tip] Аналогия
> Рейс конкретного дня в расписании.

**У нас:** `DailyPartitionsDefinition("2024-03-28", end_date="2024-07-03")` — 97 дней (конец не включается); `BackfillPolicy.multi_run(1)`: backfill 7 дней — 7 запусков, ~3 мин. Не путать с партиционированием таблиц (Iceberg) — это про хранение.

Связано: [партиционирование таблиц](partitioning.md) · [backfill](backfill.md) · [идемпотентность](idempotency.md)
