---
type: term
aliases: [incremental, is_incremental, microbatch, delete+insert, full-refresh, unique_key]
tags: [transform]
---

# Инкрементальная модель

**Модель, которая при первом запуске строится целиком, а дальше обрабатывает только новое окно и вливает его в таблицу по стратегии: append, delete+insert, merge, microbatch.** Условие окна пишется внутри `{% if is_incremental() %}`, `{{ this }}` — сама таблица; `--full-refresh` пересобирает с нуля.

> [!tip] Аналогия
> Каждый день доготавливать свежую порцию, не переделывая вчерашнее.

**У нас:** демо `fct_city_weather_daily`: delete+insert по (city_id, weather_date) с окном `lookback_days`. Microbatch с `begin` на исторических данных идёт до сегодня: 834 пачки за 143 с → нужны `--event-time-start/--event-time-end`.

Связано: [материализация](materialization.md) · [курсор](incremental-cursor.md) · [backfill](backfill.md)
