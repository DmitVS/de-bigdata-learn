"""Учебные трансформации погоды (урок 05): чистые функции DataFrame → DataFrame.

Функция не читает файлы и не пишет таблицы — только преобразует вход. Поэтому её можно
проверить на трёх строках, собранных в тесте, а в продакшене подать ей весь датасет.
"""

from pyspark.sql import Column, DataFrame
from pyspark.sql import functions as F


def city_weather_daily(raw: DataFrame) -> DataFrame:
    """Погода по городу за день: среднее по магазинам города. Grain — (city_id, weather_date)."""
    return raw.groupBy("city_id", F.to_date("dt").alias("weather_date")).agg(
        F.round(F.avg("precpt"), 3).alias("precipitation"),
        F.round(F.avg("avg_temperature"), 2).alias("avg_temperature"),
        F.countDistinct("store_id").alias("stores"),
    )


def is_rainy(precipitation: Column, threshold: float = 1.0) -> Column:
    """Дождливый день: осадки строго больше порога. NULL (нет данных) — не дождливый."""
    return F.coalesce(precipitation > F.lit(threshold), F.lit(False))


def rainy_days(daily: DataFrame, threshold: float = 1.0) -> DataFrame:
    """Число дождливых и всех дней по городу."""
    return daily.groupBy("city_id").agg(
        F.sum(is_rainy(F.col("precipitation"), threshold).cast("int")).alias("rainy_days"),
        F.count("*").alias("days"),
    )
