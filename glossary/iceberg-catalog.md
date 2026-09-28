---
type: term
aliases: [Каталог, Iceberg-каталог, REST-каталог, Lakekeeper, warehouse, namespace]
tags: [lakehouse]
---

# Iceberg REST-каталог (Lakekeeper)

**Сервер, который хранит соответствие `namespace.таблица → текущий metadata.json`** в
транзакционной базе и атомарно переключает этот указатель при записи. Клиенты говорят с ним по
стандартному HTTP API **Iceberg REST**, поэтому любой движок работает с любым REST-каталогом.

- **Namespace** — группа таблиц (аналог схемы).
- **Warehouse** — связка каталога с хранилищем: storage-profile (где: endpoint, бакет, префикс)
  + storage-credential (чем открывать).
- Выдаёт клиентам адрес S3 и [временные ключи](vended-credentials.md).

> [!tip] Аналогия
> Картотека у входа на склад: «sales → актуальная опись №00002» + бюро пропусков.

**У нас:** Lakekeeper, API `http://lakekeeper:8181/catalog`, база `lakekeeper` в Postgres,
warehouse `lakehouse` создаёт `infra/docker/lakekeeper/init.sh`.

Связано: [Iceberg](iceberg.md) · [vended credentials](vended-credentials.md)
