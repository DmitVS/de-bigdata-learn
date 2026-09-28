---
type: term
aliases: [localhost, loopback, 127.0.0.1]
tags: [сеть]
---

# localhost (loopback)

**Имя, которое всегда означает «это же устройство»**. Ему соответствует адрес `127.0.0.1` на
специальном [интерфейсе](network-interface.md) `lo` (loopback, «петля»): данные никуда не
уходят и возвращаются в ту же систему.

> [!tip] Аналогия
> «Позвонить самому себе». Куда попадёшь — зависит от того, **откуда** звонишь.

> [!warning] Главное для Docker
> У каждого контейнера свой `localhost` (см. [namespace](network-namespace.md)). В контейнере
> `workspace` `localhost:9000` — это сам `workspace`, а не хост и не Silo.

**Проверить:** `make shell`, затем `curl -s localhost:9000; echo $?` → `7` (никто не слушает).

Связано: [IP-адрес](ip-address.md) · [публикация порта](port-publishing.md)
