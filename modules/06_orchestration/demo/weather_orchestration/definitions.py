"""Точка входа code location `weather_demo`: всё, что Dagster знает об этом проекте.

Code-сервер (сервис dagster-demo) загружает этот модуль: `dagster code-server start -m
weather_orchestration.definitions`. Урок 02, шаг 3.
"""

from dagster import Definitions, load_assets_from_modules
from dagster_dbt import DbtCliResource
from dagster_dlt import DagsterDltResource

from . import checks
from .assets import bronze, landing, report, transform
from .automation import (
    landing_inventory_job,
    landing_sales_sensor,
    transform_job,
    transform_schedule,
    weather_daily_job,
    weather_daily_schedule,
)
from .resources import DuckDBResource, S3Resource

defs = Definitions(
    assets=load_assets_from_modules([landing, bronze, transform, report]),
    asset_checks=[checks.weather_bronze_all_cities],
    jobs=[weather_daily_job, transform_job, landing_inventory_job],
    schedules=[weather_daily_schedule, transform_schedule],
    sensors=[landing_sales_sensor],
    resources={
        "s3": S3Resource(),
        "duck": DuckDBResource(),
        "dlt": DagsterDltResource(),
        "dbt": DbtCliResource(project_dir=transform.dbt_project),
    },
)
