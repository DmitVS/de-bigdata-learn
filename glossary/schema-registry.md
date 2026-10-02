---
type: term
aliases: [Schema Registry, реестр схем, Avro, субъект, subject, совместимость схем, BACKWARD, FORWARD, FULL]
tags: [streaming]
---

# Schema Registry и Avro

**Avro — двоичный формат со схемой; схемы хранятся в реестре по субъектам (`<топик>-value`) с версиями, а сообщение начинается с магического байта и ID схемы. При регистрации новой версии реестр проверяет совместимость (по умолчанию BACKWARD: удалять поля и добавлять поля со значением по умолчанию).**

> [!tip] Аналогия
> Нотариус бланков: хранит редакции и не регистрирует ту, которую не прочтут старые получатели.

**У нас:** реестр встроен в Redpanda — `http://redpanda:8081`; демо `--avro` пишет в `demo.weather_readings.avro`; проверка — `POST /compatibility/subjects/<s>/versions/latest`.

Связано: [эволюция схемы](schema-evolution.md) · [контракт данных](data-contract.md)
