---
type: term
aliases: [broadcast join, broadcast hash join, sort-merge join, shuffle hash join, autoBroadcastJoinThreshold]
tags: [batch]
---

# Соединения в Spark

**Broadcast hash join рассылает маленькую сторону всем executors и не перемешивает большую; sort-merge join перемешивает обе стороны по ключу, сортирует и сливает; shuffle hash join перемешивает обе и строит хеш-таблицу по меньшей.** Broadcast выбирается, если сторона меньше `autoBroadcastJoinThreshold` (10 МБ), по подсказке `F.broadcast()` или AQE после выяснения размера.

> [!tip] Аналогия
> Раздать копию короткого списка каждому или развезти оба длинных по фамилиям.

**У нас:** почасовые продажи × города: sort-merge 12 с, broadcast 1,1 с. Соединение с `distinct` справочником в `explain()` — SortMergeJoin (размер неизвестен), в итоговом плане — broadcast.

Связано: [join](join.md) · [shuffle](shuffle.md) · [перекос](data-skew.md)
