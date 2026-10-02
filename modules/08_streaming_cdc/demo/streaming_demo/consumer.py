"""Учебный consumer (модуль 08, урок 02): читает топик в группе и печатает, откуда пришло.

    python -m streaming_demo.consumer --group demo-a --max 5
    python -m streaming_demo.consumer --group demo-a --max 5        # продолжит с коммита
    python -m streaming_demo.consumer --group demo-b --max 5        # новая группа — с начала

Офсеты коммитятся вручную после обработки сообщения: так падение между чтением и обработкой
приведёт к повтору (at-least-once), а не к потере.
"""

import argparse
import time

from confluent_kafka import Consumer


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--topic", default="demo.weather_readings")
    parser.add_argument("--group", required=True)
    parser.add_argument("--max", type=int, default=10)
    args = parser.parse_args()

    consumer = Consumer(
        {
            "bootstrap.servers": "redpanda:9092",
            "group.id": args.group,
            "auto.offset.reset": "earliest",  # у новой группы нет офсетов — читать с начала
            "enable.auto.commit": False,
        }
    )
    consumer.subscribe([args.topic])
    seen = 0
    # Вход в группу и назначение партиций занимают секунды: первое сообщение ждём дольше
    deadline = time.time() + 20
    while seen < args.max:
        msg = consumer.poll(1.0)
        if msg is None:
            if seen or time.time() > deadline:
                break
            continue
        if msg.error():
            print("ошибка:", msg.error())
            continue
        print(f"партиция {msg.partition()} офсет {msg.offset()} ключ {msg.key().decode()}")
        consumer.commit(message=msg, asynchronous=False)
        seen += 1
    consumer.close()


if __name__ == "__main__":
    main()
