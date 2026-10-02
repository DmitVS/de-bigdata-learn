---
type: term
aliases: [Spark Connect, pyspark-client, sc://]
tags: [batch]
---

# Spark Connect

**Режим, в котором клиент — тонкая библиотека без JVM — отправляет план DataFrame по gRPC серверу, а сервер (он же driver) выполняет его и возвращает результат в Arrow.** Нет RDD API и `sparkContext`; Python UDF выполняются на executors, и версия Python там должна совпадать с клиентом.

> [!tip] Аналогия
> Окно прорабской: чертёж передают в окно, бригада клиенту не нужна.

**У нас:** `SparkSession.builder.remote("sc://spark-connect:15002").getOrCreate()` или `get_spark()` из `modules/07_batch_spark/demo/spark_demo/session.py`; в workspace — `pyspark-client` 4.1.3. Driver долгоживущий, поэтому UI 4040 хранит прошлые запросы.

Связано: [Spark](spark.md) · [Arrow](arrow.md)
