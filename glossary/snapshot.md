---
type: term
aliases: [Snapshot, снимок, версия таблицы, time travel]
tags: [lakehouse]
---

# Snapshot (версия таблицы)

**Состояние [Iceberg](iceberg.md)-таблицы на момент одной записи**: какой набор data-файлов её
составляет. Каждый `append`, `overwrite`, `delete` создаёт новый snapshot; все они перечислены в
`metadata.json`, один из них — текущий.

**Time travel** — прочитать таблицу по старому snapshot'у: `table.scan(snapshot_id=…)`. **Откат**
— сделать старый snapshot текущим. Старые snapshot'ы со временем удаляют вместе с их файлами
(обслуживание таблицы, модуль 03).

> [!tip] Аналогия
> Версии описи склада: №1 — две коробки, №2 — те же две плюс третья.

Связано: [Iceberg](iceberg.md)
