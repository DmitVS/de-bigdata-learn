---
type: term
aliases: [Том, named volume, volume]
tags: [docker]
---

# Том (named volume)

**Хранилище данных, которым управляет Docker и которое живёт отдельно от контейнеров.**
Монтируется в папку контейнера: процесс пишет туда как в обычную папку, а файлы попадают в том,
а не в слой записи. Переживает пересоздание контейнеров, обновление образов, `make restart`.
Удаляется только явно: `docker compose down -v` (`make clean`).

> [!tip] Аналогия
> Сейф в архиве здания: кабинет снесли и обставили заново — сейф на месте.

**Запись:** `postgres-data:/var/lib/postgresql/data` — слева имя без `/`. Имя объявляется в
секции `volumes:` верхнего уровня, compose добавляет префикс проекта: `debd_postgres-data`.

**У нас:** `debd_postgres-data` (данные Postgres), `debd_silo-data` (объекты S3).

**Посмотреть:** `docker volume ls`, `docker volume inspect debd_postgres-data`.

Связано: [bind mount](bind-mount.md) · [контейнер](container.md)
