"""Генератор изменений в учётной системе сети `retail_oltp` (эмуляция работы приложения).

Модуль 04 (лабы 04.2, 04.3), модуль 05 (snapshots), модуль 08 (CDC). Работает поверх схемы из
контракта лабы 04.2: таблицы `stores`, `products`, `assortment` с колонкой `updated_at`.

Что делает за один запуск (`--changes N` случайных операций, `--seed` для повторяемости):
- `store_status`   — магазин закрывается или снова открывается (UPDATE, updated_at = now());
- `recategorize`   — товар переносят в другую категорию третьего уровня той же категории
                     второго уровня. Так делает «старый модуль» приложения: UPDATE **без**
                     изменения updated_at (если в базе нет триггера, который его выставит);
- `delist`         — товар убирают из ассортимента магазина (DELETE — строки больше нет);
- `list`           — товар добавляют в ассортимент магазина (INSERT);
- `new_store`      — открывается новый магазин в существующем городе (INSERT в stores и
                     копия ассортимента соседнего магазина того же города).

Режим `--slow-tx SECONDS`: одна транзакция меняет статус магазина с updated_at = now() и
фиксируется только через SECONDS секунд — так выглядит долгая транзакция приложения.
Режим `--loop SECONDS`: повторять пачку изменений каждые SECONDS секунд (для CDC в модуле 08).

Запуск (в workspace):
    python scripts/retail_oltp_changes.py --changes 20 --seed 1
    python scripts/retail_oltp_changes.py --slow-tx 30
    python scripts/retail_oltp_changes.py --changes 5 --loop 10
"""

import argparse
import os
import random
import time
from collections import Counter

import psycopg

OPERATIONS = ["store_status", "recategorize", "delist", "list", "new_store"]
WEIGHTS = [3, 3, 3, 3, 1]


def connect() -> psycopg.Connection:
    return psycopg.connect(
        host=os.environ["POSTGRES_HOST"],
        dbname=os.environ.get("RETAIL_OLTP_DB", "retail_oltp"),
        user=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
    )


def store_status(cur: psycopg.Cursor, rnd: random.Random) -> str:
    store_id, status = cur.execute(
        "SELECT store_id, status FROM stores ORDER BY random() LIMIT 1"
    ).fetchone()
    new_status = "closed" if status == "open" else "open"
    cur.execute(
        "UPDATE stores SET status = %s, updated_at = now() WHERE store_id = %s",
        (new_status, store_id),
    )
    return f"store {store_id}: {status} → {new_status}"


def recategorize(cur: psycopg.Cursor, rnd: random.Random) -> str:
    row = cur.execute(
        """
        SELECT p.product_id, p.third_category_id, alt.third_category_id
        FROM products p
        JOIN LATERAL (
            SELECT DISTINCT third_category_id FROM products o
            WHERE o.second_category_id = p.second_category_id
              AND o.third_category_id <> p.third_category_id
            ORDER BY third_category_id LIMIT 1
        ) alt ON true
        ORDER BY random() LIMIT 1
        """
    ).fetchone()
    if row is None:
        return "recategorize: нет подходящего товара"
    product_id, old, new = row
    # «Старый модуль»: updated_at не трогает
    cur.execute(
        "UPDATE products SET third_category_id = %s WHERE product_id = %s", (new, product_id)
    )
    return f"product {product_id}: third_category {old} → {new} (без updated_at)"


def delist(cur: psycopg.Cursor, rnd: random.Random) -> str:
    row = cur.execute(
        "SELECT store_id, product_id FROM assortment ORDER BY random() LIMIT 1"
    ).fetchone()
    cur.execute("DELETE FROM assortment WHERE store_id = %s AND product_id = %s", row)
    return f"assortment: удалён товар {row[1]} в магазине {row[0]}"


def list_product(cur: psycopg.Cursor, rnd: random.Random) -> str:
    row = cur.execute(
        """
        SELECT s.store_id, p.product_id FROM stores s CROSS JOIN products p
        WHERE NOT EXISTS (SELECT 1 FROM assortment a
                          WHERE a.store_id = s.store_id AND a.product_id = p.product_id)
        ORDER BY random() LIMIT 1
        """
    ).fetchone()
    cur.execute(
        "INSERT INTO assortment (store_id, product_id, listed_on, updated_at) "
        "VALUES (%s, %s, current_date, now())",
        row,
    )
    return f"assortment: добавлен товар {row[1]} в магазин {row[0]}"


def new_store(cur: psycopg.Cursor, rnd: random.Random) -> str:
    max_id, donor, city_id = cur.execute(
        """
        SELECT (SELECT max(store_id) FROM stores), store_id, city_id
        FROM stores WHERE status = 'open' ORDER BY random() LIMIT 1
        """
    ).fetchone()
    store_id = max_id + 1
    cur.execute(
        "INSERT INTO stores (store_id, city_id, status, opened_on, updated_at) "
        "VALUES (%s, %s, 'open', current_date, now())",
        (store_id, city_id),
    )
    cur.execute(
        "INSERT INTO assortment (store_id, product_id, listed_on, updated_at) "
        "SELECT %s, product_id, current_date, now() FROM assortment WHERE store_id = %s",
        (store_id, donor),
    )
    return f"stores: новый магазин {store_id} в городе {city_id} (ассортимент как у {donor})"


HANDLERS = {
    "store_status": store_status,
    "recategorize": recategorize,
    "delist": delist,
    "list": list_product,
    "new_store": new_store,
}


def run_batch(changes: int, rnd: random.Random) -> None:
    counts: Counter[str] = Counter()
    with connect() as conn, conn.cursor() as cur:
        # random() в Postgres тоже от зерна — иначе --seed не даёт повторяемости
        cur.execute("SELECT setseed(%s)", (rnd.random(),))
        for _ in range(changes):
            op = rnd.choices(OPERATIONS, WEIGHTS)[0]
            print(HANDLERS[op](cur, rnd))
            counts[op] += 1
    print("Итого:", dict(counts))


def slow_transaction(seconds: int) -> None:
    with connect() as conn, conn.cursor() as cur:
        store_id, status = cur.execute(
            "SELECT store_id, status FROM stores ORDER BY random() LIMIT 1"
        ).fetchone()
        new_status = "closed" if status == "open" else "open"
        cur.execute(
            "UPDATE stores SET status = %s, updated_at = now() "
            "WHERE store_id = %s RETURNING updated_at",
            (new_status, store_id),
        )
        updated_at = cur.fetchone()[0]
        print(f"store {store_id}: {status} → {new_status}, updated_at = {updated_at}")
        print(f"транзакция открыта, фиксация через {seconds} с…", flush=True)
        time.sleep(seconds)
    print("зафиксировано")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--changes", type=int, default=10, help="число операций в пачке")
    parser.add_argument("--seed", type=int, help="зерно случайности для повторяемости")
    parser.add_argument("--slow-tx", type=int, metavar="SECONDS", help="долгая транзакция")
    parser.add_argument("--loop", type=int, metavar="SECONDS", help="повторять пачки")
    args = parser.parse_args()

    if args.slow_tx:
        slow_transaction(args.slow_tx)
        return
    rnd = random.Random(args.seed)
    while True:
        run_batch(args.changes, rnd)
        if not args.loop:
            break
        time.sleep(args.loop)


if __name__ == "__main__":
    main()
