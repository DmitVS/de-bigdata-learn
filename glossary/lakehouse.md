---
type: term
aliases: [Lakehouse, озеро данных, data lake]
tags: [архитектура]
---

# Lakehouse

**Архитектура, где хранение, формат и вычисления разделены**: данные лежат в дешёвом
объектном хранилище ([S3](s3.md)) в открытых форматах ([Parquet](parquet.md) +
[Iceberg](iceberg.md)), а читают и пишут их разные движки (DuckDB, Spark, Trino) через общий
[каталог](iceberg-catalog.md).

Отличие от **data lake** («просто файлы в S3»): у lakehouse есть таблицы, схемы, транзакции и
версии. Отличие от **хранилища данных** (Snowflake, Postgres): данные не заперты внутри одной
программы.

> [!tip] Аналогия
> Общий склад с описями и картотекой, куда могут приезжать грузовики разных компаний.

**У нас:** Silo + Iceberg + Lakekeeper; движки — PyIceberg и DuckDB, позже Spark (07), Trino (10).

Связано: [Iceberg](iceberg.md) · [каталог](iceberg-catalog.md) · [warehouse, lake, lakehouse](warehouse-lake-lakehouse.md) · [medallion](medallion.md)
