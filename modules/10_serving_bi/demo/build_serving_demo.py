"""Учебные витрины модуля 10: звезда продаж в Iceberg и справочник магазинов в Postgres.

Модуль 10 отдаёт витрины бизнесу, поэтому ему нужны готовые витрины. Свои витрины capstone ты
строишь в модулях 05–07; этот скрипт даёт одинаковый для всех образец, на котором проверены
команды уроков. Даты и значения — как в датасете (97 дней, 2024-03-28 … 2024-07-02).

Iceberg, пространство имён serving_demo (каталог Lakekeeper):
    dim_store        898 строк    store_id, city_id
    dim_product      865 строк    product_id, management_group_id, first/second/third_category_id
    fct_sales_daily  4,85 млн     магазин × товар × день: продажи, часы без товара, скидка, промо,
                                  праздник, погода

Postgres, база retail_oltp, схема serving_demo:
    stores           898 строк    store_id, city_id, status ('open'), updated_at
                                  — текущий справочник учётной системы для федеративных запросов

Почасовая таблица для ClickHouse (108 млн строк) строится отдельно, прямо из файлов датасета:
    make ch ARGS="--queries-file modules/10_serving_bi/demo/clickhouse/01_sales_hourly.sql"

Запуск (в make shell, папка modules/10_serving_bi/demo):
    python build_serving_demo.py            # создать или пересоздать всё
    python build_serving_demo.py --drop     # удалить учебные таблицы
"""

import argparse
import os
import time

import duckdb

RAW = "/workspace/data/raw/freshretailnet_50k/data/*.parquet"
NS = "serving_demo"

TABLES = {
    "dim_store": f"""
        SELECT DISTINCT store_id::INTEGER AS store_id, city_id::INTEGER AS city_id
        FROM read_parquet('{RAW}') ORDER BY store_id
    """,
    "dim_product": f"""
        SELECT DISTINCT product_id::INTEGER AS product_id,
               management_group_id::INTEGER AS management_group_id,
               first_category_id::INTEGER AS first_category_id,
               second_category_id::INTEGER AS second_category_id,
               third_category_id::INTEGER AS third_category_id
        FROM read_parquet('{RAW}') ORDER BY product_id
    """,
    "fct_sales_daily": f"""
        SELECT dt::DATE AS dt, store_id::INTEGER AS store_id, product_id::INTEGER AS product_id,
               sale_amount, stock_hour6_22_cnt AS oos_hours,
               discount, activity_flag, holiday_flag, precpt, avg_temperature
        FROM read_parquet('{RAW}') ORDER BY dt, store_id, product_id
    """,
}


def connect() -> duckdb.DuckDBPyConnection:
    con = duckdb.connect()
    con.execute("INSTALL iceberg; LOAD iceberg; INSTALL httpfs; LOAD httpfs; INSTALL postgres")
    con.execute(
        f"""ATTACH '{os.environ["ICEBERG_WAREHOUSE"]}' AS lh (TYPE iceberg,
            ENDPOINT '{os.environ["ICEBERG_CATALOG_URI"]}', AUTHORIZATION_TYPE 'none')"""
    )
    con.execute(
        f"""ATTACH 'host={os.environ["POSTGRES_HOST"]} dbname=retail_oltp
            user={os.environ["POSTGRES_USER"]} password={os.environ["POSTGRES_PASSWORD"]}'
            AS pg (TYPE postgres)"""
    )
    return con


def drop(con: duckdb.DuckDBPyConnection) -> None:
    for table in TABLES:
        con.execute(f"DROP TABLE IF EXISTS lh.{NS}.{table}")
    con.execute(f"CALL postgres_execute('pg', 'DROP SCHEMA IF EXISTS {NS} CASCADE')")


def build(con: duckdb.DuckDBPyConnection) -> None:
    con.execute(f"CREATE SCHEMA IF NOT EXISTS lh.{NS}")
    for table, query in TABLES.items():
        started = time.perf_counter()
        # DuckDB не умеет CREATE OR REPLACE для Iceberg (модуль 05): сначала DROP
        con.execute(f"DROP TABLE IF EXISTS lh.{NS}.{table}")
        con.execute(f"CREATE TABLE lh.{NS}.{table} AS {query}")
        rows = con.sql(f"SELECT count(*) FROM lh.{NS}.{table}").fetchone()[0]
        seconds = time.perf_counter() - started
        print(f"iceberg  {NS}.{table:<16} {rows:>10,} строк  {seconds:5.1f} с")

    # Справочник учётной системы: ключ и ограничения задаём сами — CTAS через ATTACH их не создаст
    con.execute(
        f"""CALL postgres_execute('pg', '
            DROP SCHEMA IF EXISTS {NS} CASCADE;
            CREATE SCHEMA {NS};
            CREATE TABLE {NS}.stores (
                store_id   integer PRIMARY KEY,
                city_id    integer NOT NULL,
                status     text NOT NULL DEFAULT ''open'',
                updated_at timestamptz NOT NULL DEFAULT now()
            )')"""
    )
    con.execute(
        f"INSERT INTO pg.{NS}.stores (store_id, city_id) "
        f"SELECT store_id, city_id FROM lh.{NS}.dim_store"
    )
    rows = con.sql(f"SELECT count(*) FROM pg.{NS}.stores").fetchone()[0]
    print(f"postgres retail_oltp.{NS}.stores {rows:>6,} строк")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--drop", action="store_true", help="удалить учебные таблицы")
    args = parser.parse_args()

    con = connect()
    if args.drop:
        drop(con)
        print("учебные таблицы удалены")
    else:
        build(con)


if __name__ == "__main__":
    main()
