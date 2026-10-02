"""Слой report: отчёт по дождливым дням для «потребителя» — таблица в метаданных ассета."""

from dagster import AssetKey, MaterializeResult, MetadataValue, asset

from ..resources import DuckDBResource


@asset(
    deps=[AssetKey("mart_city_rainy_days")],
    group_name="report",
    kinds={"duckdb"},
    pool="duckdb",
    description="Топ-5 городов по числу дождливых дней — то, что увидел бы бизнес.",
)
def rainy_cities_report(duck: DuckDBResource) -> MaterializeResult:
    with duck.connect(read_only=True) as con:
        top = con.sql(
            "SELECT city_id, rainy_days, days FROM main.mart_city_rainy_days "
            "ORDER BY rainy_days DESC, city_id LIMIT 5"
        ).fetchall()
    lines = ["| город | дождливых дней | дней |", "|---|---|---|"]
    lines += [f"| {city} | {rainy} | {days} |" for city, rainy, days in top]
    return MaterializeResult(metadata={"top5": MetadataValue.md("\n".join(lines))})
