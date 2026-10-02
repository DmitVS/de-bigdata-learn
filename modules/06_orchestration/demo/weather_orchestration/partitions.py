"""Партиции по дням: период датасета FreshRetailNet-50K, 2024-03-28 … 2024-07-02 (97 дней).

`end_date` не включается, поэтому 2024-07-03. Без него Dagster создавал бы партиции до
сегодняшнего дня (урок 03, шаг 3).
"""

from dagster import DailyPartitionsDefinition

daily = DailyPartitionsDefinition(start_date="2024-03-28", end_date="2024-07-03")
