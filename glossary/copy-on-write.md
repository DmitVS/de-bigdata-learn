---
type: term
aliases: [Copy-on-write Iceberg, merge-on-read, delete file, файл удалений]
tags: [iceberg]
---

# Copy-on-write и merge-on-read (Iceberg)

**Два способа изменить строки в неизменяемых файлах.**

- **Copy-on-write** — переписать файл без удалённых или с изменёнными строками. Запись дорогая,
  чтение дешёвое. Так делает PyIceberg: удаление одной строки → снапшот `overwrite`,
  `deleted-data-files 1`, `added-data-files 1`.
- **Merge-on-read** — записать маленький файл удалений; исходный не трогать. Запись дешёвая, чтение
  применяет удаления. Spark, Flink; Iceberg v2.

> [!tip] Аналогия
> Переупаковать коробку без одной вещи — или приложить записку «вещь №5 не считать».

Не путать с copy-on-write слоёв Docker ([слой образа](image-layer.md)) — идея та же: оригинал не
меняется.

Связано: [snapshot](snapshot.md) · [compaction](compaction.md)
