---
type: term
aliases: [Vended credentials, STS, AssumeRole, временные ключи, session token]
tags: [lakehouse, безопасность]
---

# Vended credentials и STS

**Vended credentials** — ключи к хранилищу, которые клиент **получает от каталога** на время
работы с таблицей, а не хранит сам. **STS** (Security Token Service) — служба S3, выдающая по
постоянному ключу **временный** (access key + secret + session token) с ограниченным сроком и
правами; запрос называется **AssumeRole**.

**Механизм:** клиент → каталог (`loadTable`) → каталог root-ключом делает AssumeRole в S3 →
отдаёт клиенту config: `s3.endpoint` + временные ключи + срок + адрес для обновления.

> [!tip] Аналогия
> Мастер-ключ от склада только у завхоза; посетителю выписывают пропуск на час.

**Зачем:** root-ключ хранится в одном месте; утечка временного ключа ограничена сроком; переезд
хранилища — правка одного storage-profile. Клиенту Iceberg не нужны свои `S3_ENDPOINT`/`AWS_*`.

**У нас:** `sts-enabled: true`, срок — 3600 с (`sts-token-validity-seconds`).

Связано: [каталог](iceberg-catalog.md) · [S3](s3.md)
