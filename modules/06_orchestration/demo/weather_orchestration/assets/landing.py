"""Слой landing: файлы погоды за день в S3 и опись файлов продаж, которые кладёт источник.

- `weather_files` — «выгрузка источника»: погода по городам за день (партиция) из сырых
  файлов датасета → `s3://landing/demo_orchestration/weather/dt=…/weather.parquet`.
  Конфиг `fail_probability` имитирует нестабильный источник, чтобы увидеть ретраи (урок 01).
- `landing_sales_inventory` — опись файлов продаж, которые кладёт `scripts/landing_drop.py`:
  сколько строк и байт пришло за день. Запускается сенсором при появлении файла (урок 03).
"""

import random

import duckdb
import pyarrow.parquet as pq
from dagster import (
    AssetExecutionContext,
    BackfillPolicy,
    Backoff,
    Config,
    MaterializeResult,
    MetadataValue,
    RetryPolicy,
    asset,
)

from ..partitions import daily
from ..resources import DuckDBResource, S3Resource

RAW = "/workspace/data/raw/freshretailnet_50k/data/*.parquet"
WEATHER_PREFIX = "landing/demo_orchestration/weather"
SALES_PREFIX = "landing/freshretail/sales"


class WeatherFilesConfig(Config):
    fail_probability: float = 0.0  # доля «падений источника» на попытку, 0…1


@asset(
    partitions_def=daily,
    backfill_policy=BackfillPolicy.multi_run(1),
    group_name="landing",
    kinds={"s3", "parquet"},
    retry_policy=RetryPolicy(max_retries=3, delay=2, backoff=Backoff.EXPONENTIAL),
    description="Погода по городам за день: файл в S3 landing (выгрузка источника).",
)
def weather_files(
    context: AssetExecutionContext, config: WeatherFilesConfig, s3: S3Resource
) -> MaterializeResult:
    day = context.partition_key
    attempt = context.retry_number + 1
    if random.random() < config.fail_probability:
        raise ConnectionError(f"источник недоступен (учебный сбой), попытка {attempt}")

    table = duckdb.sql(
        f"""
        SELECT city_id, dt::DATE AS dt,
               round(avg(precpt), 3) AS precipitation,
               round(avg(avg_temperature), 2) AS avg_temperature,
               round(avg(avg_humidity), 2) AS avg_humidity,
               count(DISTINCT store_id) AS stores
        FROM read_parquet('{RAW}')
        WHERE dt = '{day}'
        GROUP BY city_id, dt
        ORDER BY city_id
        """
    ).to_arrow_table()

    path = f"{WEATHER_PREFIX}/dt={day}/weather.parquet"
    with s3.filesystem().open(path, "wb") as f:  # перезапись = идемпотентность партиции
        pq.write_table(table, f)
    context.log.info(f"{table.num_rows} городов → s3://{path} (попытка {attempt})")
    return MaterializeResult(
        metadata={"rows": table.num_rows, "path": MetadataValue.path(f"s3://{path}")}
    )


@asset(
    partitions_def=daily,
    backfill_policy=BackfillPolicy.multi_run(1),
    group_name="landing",
    kinds={"s3", "duckdb"},
    pool="duckdb",  # один писатель DuckDB во всех запусках (dagster.yaml, concurrency)
    description="Опись файлов продаж в landing: строки и размер за день.",
)
def landing_sales_inventory(
    context: AssetExecutionContext, s3: S3Resource, duck: DuckDBResource
) -> MaterializeResult:
    day = context.partition_key
    path = f"{SALES_PREFIX}/dt={day}/sales.parquet"
    fs = s3.filesystem()
    info = fs.info(path)
    rows = pq.ParquetFile(fs.open(path, "rb")).metadata.num_rows

    with duck.connect() as con:
        con.execute(
            """
            CREATE SCHEMA IF NOT EXISTS ops;
            CREATE TABLE IF NOT EXISTS ops.landing_inventory (
                dt DATE PRIMARY KEY, rows BIGINT, bytes BIGINT, modified TIMESTAMP);
            """
        )
        # INSERT OR REPLACE по ключу dt: повторная доставка файла обновляет строку, не дублирует
        con.execute(
            "INSERT OR REPLACE INTO ops.landing_inventory VALUES (?, ?, ?, ?)",
            [day, rows, info["size"], info["LastModified"].replace(tzinfo=None)],
        )
    return MaterializeResult(metadata={"rows": rows, "bytes": info["size"]})
