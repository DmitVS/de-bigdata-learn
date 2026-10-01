"""Эмуляция источника: учётная система сети выгружает продажи за день файлом в S3 `landing`.

Модуль 04 (лаба 04.1). Для каждой даты из диапазона берёт строки FreshRetailNet-50K с этим `dt`
и пишет их в `s3://landing/freshretail/sales/dt=YYYY-MM-DD/sales.parquet`. Повторный запуск
для той же даты перезаписывает файл — так выглядит повторная доставка (новое время изменения).

Запуск (в workspace):
    python scripts/landing_drop.py --from 2024-03-28 --to 2024-04-03
    python scripts/landing_drop.py --from 2024-04-04            # одна дата
    python scripts/landing_drop.py --list                       # что уже лежит в landing
    python scripts/landing_drop.py --from 2024-04-10 --drift add      # + колонка load_batch_id
    python scripts/landing_drop.py --from 2024-04-11 --drift rename   # discount → discount_ratio

Режим --drift эмулирует изменение схемы источника (урок 05 модуля 04): `add` добавляет колонку
`load_batch_id` (номер выгрузки = число дней с начала периода), `rename` переименовывает
`discount` в `discount_ratio`.
"""

import argparse
import os
from datetime import date, timedelta

import duckdb
import pyarrow.parquet as pq
import s3fs

SOURCE = "data/raw/freshretailnet_50k/data/*.parquet"
PREFIX = "landing/freshretail/sales"


def daterange(start: date, end: date):
    day = start
    while day <= end:
        yield day
        day += timedelta(days=1)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--from", dest="start", type=date.fromisoformat)
    parser.add_argument("--to", dest="end", type=date.fromisoformat)
    parser.add_argument("--list", action="store_true", help="показать файлы в landing")
    parser.add_argument("--drift", choices=["add", "rename"], help="изменить схему файла")
    args = parser.parse_args()

    fs = s3fs.S3FileSystem(endpoint_url=os.environ["S3_ENDPOINT"])
    if args.list:
        for path in sorted(fs.glob(f"{PREFIX}/*/*.parquet")):
            info = fs.info(path)
            print(f"{path}  {info['size']:>9} B  {info['LastModified']:%Y-%m-%d %H:%M:%S}")
        return
    if args.start is None:
        parser.error("нужен --from (и при желании --to)")

    con = duckdb.connect()
    for day in daterange(args.start, args.end or args.start):
        select = "*"
        if args.drift == "add":
            select = f"*, (DATE '{day}' - DATE '2024-03-28')::INTEGER AS load_batch_id"
        elif args.drift == "rename":
            select = "* RENAME (discount AS discount_ratio)"
        table = con.sql(
            f"SELECT {select} FROM read_parquet('{SOURCE}') WHERE dt = '{day}' "
            "ORDER BY store_id, product_id"
        ).to_arrow_table()
        if table.num_rows == 0:
            print(f"{day}: в датасете нет строк — пропуск")
            continue
        path = f"{PREFIX}/dt={day}/sales.parquet"
        with fs.open(path, "wb") as f:
            pq.write_table(table, f, compression="zstd")
        print(f"{day}: {table.num_rows} строк → s3://{path}")


if __name__ == "__main__":
    main()
