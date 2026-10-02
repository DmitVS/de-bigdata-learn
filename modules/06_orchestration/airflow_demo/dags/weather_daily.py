"""Тот же учебный pipeline погоды, что в Dagster (modules/06_orchestration/demo), но на Airflow 3.

Урок 05: сравнение task- и asset-подхода. Здесь единица — задача (task), а данные Airflow видит
только как «Asset», которые задачи объявляют в outlets. Логическая дата запуска (logical date)
задаёт день: запуск за 2024-04-01 обрабатывает 2024-04-01.

Запуск: make up PROFILES="airflow", UI http://localhost:8081 → DAG weather_daily → Trigger
с выбором logical date, или в контейнере: airflow dags test weather_daily 2024-04-01.
"""

from datetime import datetime

import duckdb
from airflow.sdk import Asset, dag, task

RAW = "/workspace/data/raw/freshretailnet_50k/data/*.parquet"
FILES = "/workspace/data/airflow_demo/weather"
DB = "/workspace/data/airflow_demo/weather.duckdb"

weather_bronze = Asset("duckdb://airflow_demo/bronze_weather")


@dag(
    schedule="@daily",
    start_date=datetime(2024, 3, 28),
    end_date=datetime(2024, 7, 2),
    catchup=False,  # не запускать все прошлые дни сами при включении DAG
    max_active_runs=1,  # DuckDB-файл — один писатель
    default_args={"retries": 3, "retry_delay": 2},
    tags=["module06"],
)
def weather_daily():
    @task
    def extract(ds: str | None = None) -> str:
        """Погода по городам за день → Parquet-файл (аналог ассета weather_files)."""
        import os

        os.makedirs(FILES, exist_ok=True)
        path = f"{FILES}/dt={ds}.parquet"
        duckdb.sql(
            f"""
            COPY (
                SELECT city_id, dt::DATE AS dt, round(avg(precpt), 3) AS precipitation,
                       round(avg(avg_temperature), 2) AS avg_temperature
                FROM read_parquet('{RAW}') WHERE dt = '{ds}' GROUP BY city_id, dt
            ) TO '{path}' (FORMAT parquet)
            """
        )
        return path  # уходит следующей задаче через XCom

    @task(outlets=[weather_bronze])
    def load(path: str, ds: str | None = None) -> int:
        """Загрузка дня в DuckDB с заменой (аналог weather_bronze)."""
        with duckdb.connect(DB) as con:
            con.execute(
                "CREATE TABLE IF NOT EXISTS bronze_weather AS "
                f"SELECT * FROM read_parquet('{path}') LIMIT 0"
            )
            con.execute("DELETE FROM bronze_weather WHERE dt = ?", [ds])
            con.execute(f"INSERT INTO bronze_weather SELECT * FROM read_parquet('{path}')")
            return con.sql(
                "SELECT count(*) FROM bronze_weather WHERE dt = ?", params=[ds]
            ).fetchone()[0]

    load(extract())


@dag(schedule=[weather_bronze], start_date=datetime(2024, 3, 28), catchup=False, tags=["module06"])
def rainy_report():
    """Запускается не по времени, а когда обновился Asset weather_bronze (data-aware scheduling)."""

    @task
    def report() -> list:
        with duckdb.connect(DB, read_only=True) as con:
            return con.sql(
                "SELECT city_id, count(*) FILTER (WHERE precipitation > 1) AS rainy_days "
                "FROM bronze_weather GROUP BY city_id ORDER BY rainy_days DESC LIMIT 5"
            ).fetchall()

    report()


weather_daily()
rainy_report()
