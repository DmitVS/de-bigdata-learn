"""Один запрос на трёх движках (урок 06): почасовые продажи магазин × час.

train.parquet → 4,5 млн дневных строк → explode массива hours_sale → 108 млн почасовых строк →
сумма по (store_id, hour) = 21 552 строки. Каждый движок запускается в отдельном процессе,
чтобы пиковая память не смешивалась.

Запуск (в make shell, папка modules/07_batch_spark/demo):
    python bench_hourly.py duckdb
    python bench_hourly.py polars
    python bench_hourly.py spark      # нужен make up PROFILES="spark"
"""

import resource
import sys
import time

SOURCE = "/workspace/data/raw/freshretailnet_50k/data/train.parquet"


def run_duckdb():
    import duckdb

    return duckdb.sql(
        f"""
        SELECT store_id, hour, sum(qty) AS qty
        FROM (SELECT store_id, unnest(hours_sale) AS qty,
                     generate_subscripts(hours_sale, 1) - 1 AS hour
              FROM read_parquet('{SOURCE}'))
        GROUP BY ALL
        """
    ).fetchall()


def run_polars():
    import polars as pl

    return (
        pl.scan_parquet(SOURCE)
        .select("store_id", "hours_sale")
        .with_columns(pl.int_ranges(0, pl.col("hours_sale").list.len()).alias("hour"))
        .explode("hours_sale", "hour")
        .group_by("store_id", "hour")
        .agg(pl.col("hours_sale").sum().alias("qty"))
        .collect()
    )


def run_spark():
    from pyspark.sql import functions as F
    from spark_demo.session import get_spark

    spark = get_spark()
    return (
        spark.read.parquet(SOURCE)
        .select("store_id", F.posexplode("hours_sale").alias("hour", "qty"))
        .groupBy("store_id", "hour")
        .agg(F.sum("qty").alias("qty"))
        .collect()
    )


ENGINES = {"duckdb": run_duckdb, "polars": run_polars, "spark": run_spark}

if __name__ == "__main__":
    engine = sys.argv[1]
    started = time.time()
    rows = ENGINES[engine]()
    elapsed = time.time() - started
    peak_mb = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss // 1024
    print(f"{engine}: строк {len(rows)}, {elapsed:.2f} с, пик памяти процесса {peak_mb} МБ")
