"""Проверки ассетов (asset checks): результат виден в UI рядом с ассетом (урок 04, шаг 4).

Проверка с blocking=True останавливает материализацию потомков в том же запуске, если упала с
severity ERROR, — плохие данные не уходят дальше по графу.
"""

from dagster import AssetCheckResult, AssetCheckSeverity, AssetKey, asset_check

from .resources import DuckDBResource

CITIES = 18  # городов в датасете


@asset_check(asset=AssetKey("weather_bronze"), blocking=True, pool="duckdb")
def weather_bronze_all_cities(duck: DuckDBResource) -> AssetCheckResult:
    """В каждом загруженном дне — все 18 городов."""
    with duck.connect(read_only=True) as con:
        bad_days = con.sql(
            f"SELECT dt, count(*) AS cities FROM bronze.weather "
            f"GROUP BY dt HAVING count(*) <> {CITIES} ORDER BY dt"
        ).fetchall()
        days = con.sql("SELECT count(DISTINCT dt) FROM bronze.weather").fetchone()[0]
    return AssetCheckResult(
        passed=not bad_days,
        severity=AssetCheckSeverity.ERROR,
        metadata={"days_loaded": days, "bad_days": str(bad_days[:5])},
    )
