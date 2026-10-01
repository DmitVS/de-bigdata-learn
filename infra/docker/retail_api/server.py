"""Учебный API «маркетинговой системы» сети: промо-акции FreshRetailNet-50K по дням.

Модуль 04 (урок 04, лаба 04.4). Ведёт себя как настоящий внешний API, с которым неудобно:
- ключ доступа в заголовке `X-API-Key` (значение — RETAIL_API_KEY из .env), иначе 401;
- курсорная пагинация: `next_cursor` в ответе, пока страницы не кончатся;
- лимит частоты: больше RETAIL_API_RPS запросов в секунду → 429 и заголовок Retry-After;
- случайные сбои: доля RETAIL_API_FAIL_RATE запросов → 503.

Эндпоинты:
    GET /health
    GET /v1/promotions?date=YYYY-MM-DD&limit=100&cursor=...
        → {"date": ..., "data": [{"store_id", "city_id", "items": [{"product_id", "discount"}]}],
           "next_cursor": "..." | null}

Данные: строки датасета с activity_flag = 1, сгруппированные по магазину. Порядок — по store_id.
"""

import base64
import json
import os
import random
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

import duckdb

SOURCE = os.environ.get(
    "RETAIL_API_SOURCE", "/workspace/data/raw/freshretailnet_50k/data/*.parquet"
)
API_KEY = os.environ["RETAIL_API_KEY"]
RPS = float(os.environ.get("RETAIL_API_RPS", "10"))
FAIL_RATE = float(os.environ.get("RETAIL_API_FAIL_RATE", "0.05"))
MAX_LIMIT = 500


def load_promotions() -> dict[str, list[dict]]:
    """date → список магазинов с акциями, отсортированный по store_id."""
    rows = duckdb.sql(
        f"""
        SELECT dt, store_id, any_value(city_id) AS city_id,
               list({{'product_id': product_id, 'discount': discount}} ORDER BY product_id) AS items
        FROM read_parquet('{SOURCE}')
        WHERE activity_flag = 1
        GROUP BY dt, store_id
        ORDER BY dt, store_id
        """
    ).fetchall()
    by_date: dict[str, list[dict]] = {}
    for dt, store_id, city_id, items in rows:
        by_date.setdefault(dt, []).append(
            {"store_id": store_id, "city_id": city_id, "items": items}
        )
    return by_date


class RateLimiter:
    """Корзина токенов на всех клиентов: RPS токенов в секунду, ёмкость — RPS."""

    def __init__(self, rate: float) -> None:
        self.rate = rate
        self.tokens = rate
        self.updated = time.monotonic()
        self.lock = threading.Lock()

    def allow(self) -> bool:
        with self.lock:
            now = time.monotonic()
            self.tokens = min(self.rate, self.tokens + (now - self.updated) * self.rate)
            self.updated = now
            if self.tokens >= 1:
                self.tokens -= 1
                return True
            return False


def encode_cursor(date: str, offset: int) -> str:
    return base64.urlsafe_b64encode(f"{date}|{offset}".encode()).decode()


def decode_cursor(cursor: str) -> tuple[str, int]:
    date, offset = base64.urlsafe_b64decode(cursor.encode()).decode().split("|")
    return date, int(offset)


PROMOTIONS = load_promotions()
LIMITER = RateLimiter(RPS)


class Handler(BaseHTTPRequestHandler):
    server_version = "retail-api/1.0"

    def send_json(self, status: int, body: dict, headers: dict | None = None) -> None:
        payload = json.dumps(body, ensure_ascii=False).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        for name, value in (headers or {}).items():
            self.send_header(name, value)
        self.end_headers()
        self.wfile.write(payload)

    def do_GET(self) -> None:  # noqa: N802 — имя задаёт http.server
        url = urlparse(self.path)
        if url.path == "/health":
            return self.send_json(200, {"status": "ok", "dates": len(PROMOTIONS)})
        if url.path != "/v1/promotions":
            return self.send_json(404, {"error": "not found"})
        if self.headers.get("X-API-Key") != API_KEY:
            return self.send_json(401, {"error": "missing or invalid X-API-Key"})
        if not LIMITER.allow():
            return self.send_json(429, {"error": "rate limit exceeded"}, {"Retry-After": "1"})
        if random.random() < FAIL_RATE:
            return self.send_json(503, {"error": "temporarily unavailable, retry later"})

        query = parse_qs(url.query)
        try:
            limit = min(int(query.get("limit", ["100"])[0]), MAX_LIMIT)
            if "cursor" in query:
                date, offset = decode_cursor(query["cursor"][0])
            else:
                date, offset = query["date"][0], 0
        except (KeyError, ValueError):
            return self.send_json(400, {"error": "need ?date=YYYY-MM-DD or a valid ?cursor="})

        stores = PROMOTIONS.get(date, [])
        page = stores[offset : offset + limit]
        has_more = offset + limit < len(stores)
        next_cursor = encode_cursor(date, offset + limit) if has_more else None
        return self.send_json(200, {"date": date, "data": page, "next_cursor": next_cursor})

    def log_message(self, fmt: str, *args) -> None:
        # Короткий лог: метод, путь, код ответа — видно в `make logs S=retail-api`
        print(f"{self.address_string()} {fmt % args}", flush=True)


if __name__ == "__main__":
    print(f"retail-api: {len(PROMOTIONS)} дат, RPS={RPS}, FAIL_RATE={FAIL_RATE}", flush=True)
    ThreadingHTTPServer(("0.0.0.0", 8000), Handler).serve_forever()
