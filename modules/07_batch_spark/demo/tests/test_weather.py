"""Тесты учебных трансформаций (урок 05): маленький вход → ожидаемый выход."""

import datetime as dt

import pytest
from chispa import assert_approx_df_equality, assert_df_equality
from pyspark.sql import functions as F
from spark_demo.weather import city_weather_daily, is_rainy, rainy_days

RAW_COLUMNS = "city_id long, store_id long, dt string, precpt double, avg_temperature double"


def test_city_weather_daily_averages_stores(spark):
    raw = spark.createDataFrame(
        [
            (0, 1, "2024-04-01", 2.0, 20.0),
            (0, 2, "2024-04-01", 1.0, 22.0),  # второй магазин того же города и дня
            (1, 3, "2024-04-01", 0.0, 15.0),
        ],
        RAW_COLUMNS,
    )
    expected = spark.createDataFrame(
        [(0, dt.date(2024, 4, 1), 1.5, 21.0, 2), (1, dt.date(2024, 4, 1), 0.0, 15.0, 1)],
        "city_id long, weather_date date, precipitation double, avg_temperature double, "
        "stores long",
    )
    actual = city_weather_daily(raw)
    assert_approx_df_equality(
        actual, expected, precision=1e-6, ignore_row_order=True, ignore_nullable=True
    )


@pytest.mark.parametrize(
    ("precipitation", "rainy"),
    [(1.5, True), (1.0, False), (0.0, False), (None, False)],  # граница и NULL — отдельно
)
def test_is_rainy_boundaries(spark, precipitation, rainy):
    df = spark.createDataFrame([(precipitation,)], "precipitation double")
    assert df.select(is_rainy(F.col("precipitation")).alias("r")).first().r is rainy


def test_rainy_days_counts(spark):
    daily = spark.createDataFrame(
        [(0, 2.0), (0, 0.5), (0, None), (1, 3.0)], "city_id long, precipitation double"
    )
    expected = spark.createDataFrame(
        [(0, 1, 3), (1, 1, 1)], "city_id long, rainy_days long, days long"
    )
    assert_df_equality(rainy_days(daily), expected, ignore_row_order=True, ignore_nullable=True)
