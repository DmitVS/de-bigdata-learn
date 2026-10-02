"""Задания (jobs), расписание и сенсор (урок 03).

- `weather_daily_job` — партиционированная часть pipeline: файл → bronze за один день.
- `weather_daily_schedule` — каждый день в 00:30 запускает партицию **вчерашнего** дня.
  Наши данные исторические (2024), поэтому «живых» запусков не будет: расписание проверяют
  кнопкой Test Schedule с датой из 2024 года или в Python (урок 03, шаг 2).
- `transform_job` + `transform_schedule` — dbt и отчёт после загрузки, раз в день.
- `landing_sales_sensor` — каждые 30 с смотрит в s3://landing/freshretail/sales/ и на каждый
  новый или перезаписанный файл запрашивает опись этой даты. run_key защищает от повторов.
"""

from dagster import (
    AssetSelection,
    DefaultScheduleStatus,
    DefaultSensorStatus,
    RunRequest,
    ScheduleDefinition,
    SensorEvaluationContext,
    SkipReason,
    build_schedule_from_partitioned_job,
    define_asset_job,
    sensor,
)

from .assets.landing import SALES_PREFIX, landing_sales_inventory
from .partitions import daily
from .resources import S3Resource

weather_daily_job = define_asset_job(
    "weather_daily_job",
    selection=AssetSelection.assets("weather_files", "weather_bronze"),
    partitions_def=daily,
)

transform_job = define_asset_job(
    "transform_job",
    selection=AssetSelection.groups("transform", "report"),
)

landing_inventory_job = define_asset_job(
    "landing_inventory_job",
    selection=AssetSelection.assets(landing_sales_inventory),
    partitions_def=daily,
)

weather_daily_schedule = build_schedule_from_partitioned_job(
    weather_daily_job, name="weather_daily_schedule", hour_of_day=0, minute_of_hour=30
)

transform_schedule = ScheduleDefinition(
    name="transform_schedule",
    job=transform_job,
    cron_schedule="0 2 * * *",  # 02:00 — после загрузки дня
    default_status=DefaultScheduleStatus.STOPPED,
)


@sensor(
    job=landing_inventory_job,
    minimum_interval_seconds=30,
    default_status=DefaultSensorStatus.STOPPED,  # включается в UI (урок 03, шаг 4)
)
def landing_sales_sensor(context: SensorEvaluationContext, s3: S3Resource):
    fs = s3.filesystem()
    files = sorted(fs.glob(f"{SALES_PREFIX}/dt=*/sales.parquet"))
    if not files:
        yield SkipReason(f"в s3://{SALES_PREFIX}/ пока нет файлов")
        return
    known = set(daily.get_partition_keys())
    for path in files:
        day = path.split("dt=")[1].split("/")[0]
        if day not in known:
            continue
        modified = fs.info(path)["LastModified"].isoformat()
        # run_key = дата + время изменения: тот же файл второй раз не запустит работу,
        # а перезаписанный (повторная доставка) — запустит.
        yield RunRequest(run_key=f"{day}|{modified}", partition_key=day)
