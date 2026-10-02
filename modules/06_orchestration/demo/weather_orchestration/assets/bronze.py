"""Слой bronze: dlt загружает файл погоды за день из landing в DuckDB (урок 04, шаг 2).

dlt-ресурс читает один файл партиции, а `merge` по ключу (city_id, dt) делает загрузку
идемпотентной: перезапуск партиции заменяет строки дня, а не дописывает дубли.
"""

import os

import dlt
import pyarrow.parquet as pq
import s3fs
from dagster import AssetExecutionContext, AssetKey, AssetSpec, BackfillPolicy
from dagster_dlt import DagsterDltResource, DagsterDltTranslator, dlt_assets
from dagster_dlt.translator import DltResourceTranslatorData

from ..partitions import daily
from .landing import WEATHER_PREFIX


@dlt.source(name="landing_weather")
def landing_weather_source(day: str = "2024-03-28"):
    @dlt.resource(name="weather", primary_key=["city_id", "dt"], write_disposition="merge")
    def weather():
        # dlt-источник живёт вне ресурсов Dagster, поэтому адрес и ключи — из окружения
        fs = s3fs.S3FileSystem(endpoint_url=os.environ["S3_ENDPOINT"])
        with fs.open(f"{WEATHER_PREFIX}/dt={day}/weather.parquet", "rb") as f:
            yield pq.read_table(f)  # Arrow-таблица целиком: быстро и с типами (модуль 04)

    return weather


class WeatherTranslator(DagsterDltTranslator):
    """Имя ассета и его вход: по умолчанию dlt назвал бы их dlt_landing_weather_weather и
    landing_weather_weather. Нам нужно, чтобы вход совпал с ассетом weather_files."""

    def get_asset_spec(self, data: DltResourceTranslatorData) -> AssetSpec:
        spec = super().get_asset_spec(data)
        return spec.replace_attributes(
            key=AssetKey("weather_bronze"), deps=[AssetKey("weather_files")], group_name="bronze"
        )


@dlt_assets(
    dlt_source=landing_weather_source(),
    dlt_pipeline=dlt.pipeline(
        pipeline_name="demo_orchestration_weather",
        destination=dlt.destinations.duckdb("/workspace/data/demo_orchestration.duckdb"),
        dataset_name="bronze",
    ),
    partitions_def=daily,
    backfill_policy=BackfillPolicy.multi_run(1),  # одна партиция = один запуск dlt
    dagster_dlt_translator=WeatherTranslator(),
    pool="duckdb",
)
def weather_bronze_assets(context: AssetExecutionContext, dlt: DagsterDltResource):
    yield from dlt.run(context=context, dlt_source=landing_weather_source(context.partition_key))
