---
type: term
aliases: [pagination, курсорная пагинация, offset, page number, next_cursor]
tags: [api]
---

# Пагинация

**Выдача данных API страницами со способом запросить следующую: offset/limit, номер страницы, курсор (токен из прошлого ответа), ссылка в заголовке `Link`.** Признак конца — часть контракта API. Offset и номер страницы сдвигаются при вставках; курсор — нет.

> [!tip] Аналогия
> Пачка за раз и талончик на следующую.

**У нас:** `retail-api`: `next_cursor` в ответе, пока не `null`; ~9 страниц по 100 магазинов на дату. В dlt — `JSONResponseCursorPaginator(cursor_path="next_cursor", cursor_param="cursor")`.

Связано: [HTTP](http.md) · [повторы и backoff](retry-backoff.md)
