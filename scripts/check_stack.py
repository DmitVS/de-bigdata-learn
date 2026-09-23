"""Smoke-тест слоя core: Postgres, S3 (Silo), Iceberg REST-каталог (Lakekeeper), DuckDB.

Запуск: `make check` (внутри контейнера workspace). Создаёт временную Iceberg-таблицу,
читает её через PyIceberg и DuckDB и удаляет. Ненулевой код выхода — что-то не работает.
"""

import os
import sys

import duckdb
import psycopg
import pyarrow as pa
import s3fs
from pyiceberg.catalog import load_catalog

NAMESPACE = "_smoke"
TABLE = f"{NAMESPACE}.ping"


def check_postgres() -> None:
    dsn = (
        f"host={os.environ['POSTGRES_HOST']} dbname=postgres "
        f"user={os.environ['POSTGRES_USER']} password={os.environ['POSTGRES_PASSWORD']}"
    )
    with psycopg.connect(dsn) as conn:
        dbs = {r[0] for r in conn.execute("select datname from pg_database")}
    missing = {"lakekeeper", "retail_oltp"} - dbs
    assert not missing, f"нет баз данных: {missing}"


def check_s3() -> None:
    fs = s3fs.S3FileSystem(endpoint_url=os.environ["S3_ENDPOINT"])
    buckets = set(fs.ls(""))
    missing = {"landing", "warehouse"} - buckets
    assert not missing, f"нет бакетов: {missing}"


def check_iceberg_and_duckdb() -> None:
    catalog = load_catalog(
        "lakehouse",
        type="rest",
        uri=os.environ["ICEBERG_CATALOG_URI"],
        warehouse=os.environ["ICEBERG_WAREHOUSE"],
    )
    catalog.create_namespace_if_not_exists(NAMESPACE)
    if catalog.table_exists(TABLE):
        catalog.purge_table(TABLE)

    data = pa.table({"id": pa.array([1, 2, 3], pa.int64()), "msg": ["a", "b", "c"]})
    table = catalog.create_table(TABLE, schema=data.schema)
    try:
        table.append(data)
        assert table.scan().to_arrow().num_rows == 3, "PyIceberg прочитал не 3 строки"

        con = duckdb.connect()
        con.execute("INSTALL iceberg; LOAD iceberg; INSTALL httpfs; LOAD httpfs;")
        con.execute(
            f"ATTACH '{os.environ['ICEBERG_WAREHOUSE']}' AS lh "
            f"(TYPE iceberg, ENDPOINT '{os.environ['ICEBERG_CATALOG_URI']}', "
            "AUTHORIZATION_TYPE 'none')"
        )
        (rows,) = con.execute(f"select count(*) from lh.{TABLE}").fetchone()
        assert rows == 3, f"DuckDB прочитал {rows} строк вместо 3"
    finally:
        catalog.purge_table(TABLE)
        catalog.drop_namespace(NAMESPACE)


CHECKS = [
    ("Postgres: базы lakekeeper, retail_oltp", check_postgres),
    ("S3 (Silo): бакеты landing, warehouse", check_s3),
    ("Iceberg (Lakekeeper) + DuckDB: запись/чтение таблицы", check_iceberg_and_duckdb),
]


def main() -> int:
    failed = 0
    for name, check in CHECKS:
        try:
            check()
            print(f"OK    {name}")
        except Exception as exc:  # noqa: BLE001 — smoke-тест должен пройти все проверки
            failed += 1
            print(f"FAIL  {name}: {type(exc).__name__}: {exc}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
