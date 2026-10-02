"""Учебная база модуля 09: дневные продажи магазинов с датами, сдвинутыми к «вчера».

Проверки свежести и детекторы аномалий сравнивают данные с текущим временем: «последний день
не старше суток», «объём за вчера не выбивается из прошлых недель». Датасет заканчивается
2024-07-02, поэтому даты сдвигаются так, чтобы последний день был вчерашним. Значения не
меняются — только календарь.

Таблица raw.store_sales_daily (898 магазинов × 97 дней = 87 106 строк):
    store_id, city_id, dt, sales, products, stock_hours, loaded_at

Инциденты для уроков (можно сочетать):
    --drop-day       последний день пришёл не полностью: 60 % магазинов потеряны
    --stale DAYS     загрузка остановилась: нет последних DAYS дней
    --null-city N    у N строк последнего дня пропал city_id
    --dupes          последний день загружен дважды (append без защиты)
    --negative N     у N строк последнего дня отрицательные продажи

Запуск (в make shell, папка modules/09_quality_observability/demo):
    python build_demo_db.py                 # чистые данные
    python build_demo_db.py --drop-day      # инцидент объёма
"""

import argparse
from datetime import date, timedelta

import duckdb

RAW = "/workspace/data/raw/freshretailnet_50k/data/*.parquet"
DB = "/workspace/data/demo_quality.duckdb"
LAST_SOURCE_DAY = date(2024, 7, 2)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--drop-day", action="store_true")
    parser.add_argument("--stale", type=int, default=0)
    parser.add_argument("--null-city", type=int, default=0)
    parser.add_argument("--dupes", action="store_true")
    parser.add_argument("--negative", type=int, default=0)
    args = parser.parse_args()

    shift = (date.today() - timedelta(days=1) - LAST_SOURCE_DAY).days
    con = duckdb.connect(DB)
    con.execute("CREATE SCHEMA IF NOT EXISTS raw")
    con.execute(
        f"""
        CREATE OR REPLACE TABLE raw.store_sales_daily AS
        SELECT store_id, city_id,
               (dt::DATE + INTERVAL {shift} DAY)::DATE AS dt,
               round(sum(sale_amount), 3) AS sales,
               count(*) AS products,
               sum(stock_hour6_22_cnt)::BIGINT AS stock_hours,
               NULL::TIMESTAMP AS loaded_at
        FROM read_parquet('{RAW}')
        GROUP BY store_id, city_id, dt
        ORDER BY dt, store_id
        """
    )
    last = con.sql("SELECT max(dt) FROM raw.store_sales_daily").fetchone()[0]
    # Время загрузки дня: ночная выгрузка через 1–5 ч после конца дня; в каждый 13-й день
    # (кроме последнего) выгрузка задержалась ещё на 12 ч — материал для SLO свежести (урок 05).
    con.execute(
        f"""
        UPDATE raw.store_sales_daily
        SET loaded_at = dt + INTERVAL 1 DAY
            + to_minutes((60 + hash(dt::VARCHAR) % 240)::BIGINT)
            + CASE WHEN hash(dt::VARCHAR) % 13 = 0 AND dt < DATE '{last}'
                   THEN INTERVAL 12 HOUR ELSE INTERVAL 0 HOUR END
        """
    )

    if args.stale:
        con.execute(f"DELETE FROM raw.store_sales_daily WHERE dt > DATE '{last}' - {args.stale}")
        last = con.sql("SELECT max(dt) FROM raw.store_sales_daily").fetchone()[0]
    if args.drop_day:
        con.execute(
            f"DELETE FROM raw.store_sales_daily "
            f"WHERE dt = DATE '{last}' AND hash(store_id) % 10 < 6"
        )
    if args.null_city:
        con.execute(
            f"""UPDATE raw.store_sales_daily SET city_id = NULL
                WHERE dt = DATE '{last}' AND store_id IN (
                  SELECT store_id FROM raw.store_sales_daily WHERE dt = DATE '{last}'
                  ORDER BY store_id LIMIT {args.null_city})"""
        )
    if args.negative:
        con.execute(
            f"""UPDATE raw.store_sales_daily SET sales = -sales
                WHERE dt = DATE '{last}' AND sales > 0 AND store_id IN (
                  SELECT store_id FROM raw.store_sales_daily WHERE dt = DATE '{last}'
                  AND sales > 0 ORDER BY store_id LIMIT {args.negative})"""
        )
    if args.dupes:
        con.execute(
            f"INSERT INTO raw.store_sales_daily SELECT * FROM raw.store_sales_daily "
            f"WHERE dt = DATE '{last}'"
        )

    rows, days, first, last = con.sql(
        "SELECT count(*), count(DISTINCT dt), min(dt), max(dt) FROM raw.store_sales_daily"
    ).fetchone()
    print(f"{DB}: raw.store_sales_daily — {rows} строк, {days} дней, {first} … {last}")
    con.close()


if __name__ == "__main__":
    main()
