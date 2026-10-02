---
type: term
aliases: [code location, code-сервер, code server, Definitions, workspace.yaml, gRPC]
tags: [orchestration]
---

# Code location

**Проект Dagster с его объектом `Definitions` и окружением, загруженный отдельным процессом — code-сервером. Webserver и daemon обращаются к нему по gRPC и не импортируют код сами, поэтому ошибка или конфликт версий в одном проекте не ломают оркестратор.** Список — в `workspace.yaml`.

> [!tip] Аналогия
> Отдельное депо со своими составами; диспетчерская звонит туда по телефону.

**У нас:** сервис `dagster-demo` (`dagster code-server start -m weather_orchestration.definitions`, порт 4000), наследует окружение workspace через `extends` и `ports: !reset []`. Новый код — Deployment → Reload. Capstone — второй сервис (лаба 06.1).

Связано: [оркестратор](orchestrator.md) · [DNS](dns.md)
