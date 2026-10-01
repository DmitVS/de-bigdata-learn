---
type: term
aliases: [Apache Arrow, Arrow, PyArrow, zero-copy, RecordBatch]
tags: [хранение, python]
---

# Apache Arrow

**Стандарт раскладки колоночных данных в памяти.** Раз раскладка одна, библиотеки передают друг
другу указатель на буферы без копирования (**zero-copy**): DuckDB → Arrow → Polars, PyIceberg.

Объекты PyArrow: `Array` (колонка), `RecordBatch` (порция), `Table` (таблица), `Schema`,
`RecordBatchReader` (поток порций).

> [!tip] Аналогия
> Одинаковая раскладка на рабочем столе у всех работников: стол передают, не перекладывая вещи.

**У нас:** DuckDB → Arrow 195 мс, Arrow → Polars 17 мс; 200 тыс. строк → Python-словари 152 мс —
не переводить данные в объекты Python построчно.

**Ловушка:** в DuckDB 1.5 `.arrow()` — поток; нужна таблица — `.to_arrow_table()`.

Связано: [Parquet](parquet.md) · [форматы файлов](file-formats.md)
