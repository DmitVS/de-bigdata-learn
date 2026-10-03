"""Учебная задача Spark модуля 11: файлы датасета → bronze → агрегат по магазину и дню.

Задача нужна ради lineage: её запускает сервис spark-lineage с агентом OpenLineage, и события
запуска (входы, выходы, колонки) попадают в OpenMetadata и в data/openlineage/events.jsonl.

Два действия — два ребра графа:
    1. файлы датасета → lh.governance_demo.raw_sales (4,85 млн строк, как есть);
    2. raw_sales → lh.governance_demo.store_sales_daily (магазин × день, 87 106 строк).
OpenMetadata понимает только датасеты-таблицы: ребро от файлов он не построит, а ребро
raw_sales → store_sales_daily — построит (урок 03).

Запуск (на хосте): make spark-lineage
"""

from pyspark.sql import SparkSession
from pyspark.sql import functions as F

RAW = "/workspace/data/raw/freshretailnet_50k/data/*.parquet"
BRONZE = "lh.governance_demo.raw_sales"
TARGET = "lh.governance_demo.store_sales_daily"

spark = SparkSession.builder.appName("store_sales_daily").getOrCreate()
spark.sql("CREATE NAMESPACE IF NOT EXISTS lh.governance_demo")

(
    spark.read.parquet(RAW)
    .select("store_id", "city_id", "product_id", "dt", "sale_amount", "stock_hour6_22_cnt")
    .writeTo(BRONZE)
    .using("iceberg")
    .createOrReplace()
)

daily = (
    spark.table(BRONZE)
    .groupBy("store_id", "city_id", F.to_date("dt").alias("dt"))
    .agg(
        F.round(F.sum("sale_amount"), 3).alias("sales"),
        F.sum("stock_hour6_22_cnt").cast("int").alias("oos_hours"),
        F.count("*").cast("int").alias("products"),
    )
)
daily.writeTo(TARGET).using("iceberg").createOrReplace()
print(BRONZE, spark.table(BRONZE).count(), "строк;", TARGET, spark.table(TARGET).count(), "строк")
spark.stop()
