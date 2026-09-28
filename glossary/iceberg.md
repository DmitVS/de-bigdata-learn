---
type: term
aliases: [Iceberg, Apache Iceberg, табличный формат, metadata.json, manifest]
tags: [хранение, lakehouse]
---

# Apache Iceberg

**Открытый табличный формат**: соглашение о файлах метаданных, которые превращают набор
[Parquet](parquet.md)-файлов в S3 в таблицу со схемой, версиями и транзакциями.

**Дерево:** [каталог](iceberg-catalog.md) → `metadata.json` (схема, список
[snapshot'ов](snapshot.md)) → manifest list (одна версия) → manifest (data-файлы + min/max) →
data-файлы.

**Запись:** новые файлы никогда не меняют старые; новый `metadata.json` + атомарное
переключение указателя в каталоге. Отсюда ACID, time travel, откат, конфликт-и-повтор при
параллельной записи.

> [!tip] Аналогия
> Опись склада: «таблица sales, версия 2 = вот эти коробки». Коробки, которых нет в описи,
> к таблице не относятся.

**У нас:** таблицы в `s3://warehouse/lakehouse/<uuid таблицы>/{data,metadata}/`.

Связано: [snapshot](snapshot.md) · [каталог](iceberg-catalog.md) · [lakehouse](lakehouse.md)
