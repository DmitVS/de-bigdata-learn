"""Слой transform: dbt-проект dbt_weather как ассеты Dagster (урок 04, шаг 3).

Каждая модель dbt становится ассетом, а тесты dbt — проверками (asset checks). Источник dbt
`bronze.weather` сопоставлен с ассетом `weather_bronze`, поэтому граф сквозной: от файла в
landing до витрины.
"""

from pathlib import Path
from typing import Any

from dagster import AssetExecutionContext, AssetKey
from dagster_dbt import DagsterDbtTranslator, DbtCliResource, DbtProject, dbt_assets

DBT_DIR = Path(__file__).parents[2] / "dbt_weather"

dbt_project = DbtProject(project_dir=DBT_DIR, profiles_dir=DBT_DIR)
# manifest.json собирается при каждой загрузке code location (dbt parse, ~3 с), поэтому
# правки моделей видны после Reload в UI без отдельной команды.
dbt_project.preparer.prepare(dbt_project)


class WeatherDbtTranslator(DagsterDbtTranslator):
    def get_asset_key(self, dbt_resource_props: dict[str, Any]) -> AssetKey:
        if dbt_resource_props["resource_type"] == "source":
            return AssetKey("weather_bronze")  # source bronze.weather = ассет dlt
        return super().get_asset_key(dbt_resource_props)

    def get_group_name(self, dbt_resource_props: dict[str, Any]) -> str | None:
        return "transform"


@dbt_assets(
    manifest=dbt_project.manifest_path,
    dagster_dbt_translator=WeatherDbtTranslator(),
    pool="duckdb",
)
def weather_dbt_assets(context: AssetExecutionContext, dbt: DbtCliResource):
    yield from dbt.cli(["build"], context=context).stream()
