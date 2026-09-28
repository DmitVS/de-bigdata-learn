---
type: term
aliases: [depends_on, зависимость сервисов, condition]
tags: [docker, compose]
---

# depends_on

**Ключ compose: «запускай этот сервис, только когда у соседа выполнено условие».** Compose
строит из всех `depends_on` граф и запускает каждый контейнер, как только выполнены **его**
условия.

| Условие | Ждёт |
|---|---|
| `service_started` (по умолчанию) | сосед запущен — почти бесполезно |
| `service_healthy` | [healthcheck](healthcheck.md) соседа стал `healthy` |
| `service_completed_successfully` | one-shot сосед вышел с [кодом](exit-code.md) 0 |

> [!tip] Аналогия
> «Не начинать, пока бухгалтерия не ответит вахтёру „да“» / «…пока подрядчик не сдаст работу».

Если условие не выполнилось (сосед `unhealthy` или вышел с ошибкой), зависимый не запускается,
`up` падает. Без нужной зависимости возникает [гонка](race-condition.md).

Связано: [healthcheck](healthcheck.md) · [гонка](race-condition.md)
