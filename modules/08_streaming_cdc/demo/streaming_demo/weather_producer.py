"""Учебный producer (модуль 08): показания погоды магазинов как поток событий.

Каждый магазин раз в день «присылает» показание: осадки и температуру из FreshRetailNet-50K,
время события — детерминированный час дня от 6 до 22 (по store_id и дате). Ключ сообщения —
city_id: все показания города попадают в одну партицию и читаются по порядку.

Это не продажи и не out-of-stock — их «проигрывает» твой producer в лабе 08.2.

Запуск (в make shell, папка modules/08_streaming_cdc/demo):
    python -m streaming_demo.weather_producer --from 2024-04-01 --to 2024-04-03
    python -m streaming_demo.weather_producer --from 2024-04-01 --late 0.05  # 5 % опоздают
    python -m streaming_demo.weather_producer --from 2024-04-01 --avro  # Avro + Schema Registry
"""

import argparse
import json
import random
import zlib
from datetime import date, datetime, timedelta

import duckdb
from confluent_kafka import Producer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroSerializer
from confluent_kafka.serialization import MessageField, SerializationContext

BOOTSTRAP = "redpanda:9092"
REGISTRY = "http://redpanda:8081"
RAW = "/workspace/data/raw/freshretailnet_50k/data/*.parquet"

AVRO_SCHEMA = json.dumps(
    {
        "type": "record",
        "name": "WeatherReading",
        "namespace": "debd.demo",
        "fields": [
            {"name": "store_id", "type": "long"},
            {"name": "city_id", "type": "long"},
            {"name": "event_time", "type": "string"},
            {"name": "precipitation", "type": ["null", "double"], "default": None},
            {"name": "temperature", "type": ["null", "double"], "default": None},
        ],
    }
)


def event_hour(store_id: int, day: str) -> int:
    """Час показания 6…22, одинаковый при каждом запуске (crc32, а не random)."""
    return 6 + zlib.crc32(f"{store_id}|{day}".encode()) % 17


def readings(start: date, end: date):
    rows = duckdb.sql(
        f"""
        SELECT DISTINCT store_id, city_id, dt, precpt, avg_temperature
        FROM read_parquet('{RAW}')
        WHERE dt BETWEEN '{start}' AND '{end}'
        """
    ).fetchall()
    events = []
    for store_id, city_id, dt, precpt, temperature in rows:
        ts = datetime.fromisoformat(dt) + timedelta(hours=event_hour(store_id, dt))
        events.append(
            {
                "store_id": store_id,
                "city_id": city_id,
                "event_time": ts.isoformat(sep=" "),
                "precipitation": precpt,
                "temperature": temperature,
            }
        )
    events.sort(key=lambda e: (e["event_time"], e["store_id"]))  # порядок времени события
    return events


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--from", dest="start", type=date.fromisoformat, required=True)
    parser.add_argument("--to", dest="end", type=date.fromisoformat)
    parser.add_argument("--topic", default="demo.weather_readings")
    parser.add_argument("--late", type=float, default=0.0, help="доля событий, отправленных позже")
    parser.add_argument("--avro", action="store_true", help="Avro со схемой в Schema Registry")
    parser.add_argument("--seed", type=int, default=1)
    args = parser.parse_args()

    events = readings(args.start, args.end or args.start)
    rnd = random.Random(args.seed)
    late = []
    if args.late:
        # «Опоздавшие» события: переносим в конец потока — время события старое, приходят последними
        flags = [rnd.random() < args.late for _ in events]
        late = [e for e, f in zip(events, flags, strict=True) if f]
        events = [e for e, f in zip(events, flags, strict=True) if not f] + late

    producer = Producer({"bootstrap.servers": BOOTSTRAP, "enable.idempotence": True})
    if args.avro:
        serializer = AvroSerializer(SchemaRegistryClient({"url": REGISTRY}), AVRO_SCHEMA)
        topic = args.topic + ".avro"

        def encode(e):
            return serializer(e, SerializationContext(topic, MessageField.VALUE))
    else:
        topic = args.topic

        def encode(e):
            return json.dumps(e).encode()

    for e in events:
        producer.produce(topic, key=str(e["city_id"]).encode(), value=encode(e))
        producer.poll(0)  # отдаём управление колбэкам доставки, не копим очередь
    left = producer.flush(30)
    print(f"{len(events)} событий → {topic} (опоздавших {len(late)}), не доставлено {left}")


if __name__ == "__main__":
    main()
