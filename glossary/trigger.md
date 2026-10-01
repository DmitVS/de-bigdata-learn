---
type: term
aliases: [trigger, триггер, BEFORE UPDATE, plpgsql]
tags: [postgres]
---

# Триггер

**Функция, которую база вызывает сама при событии над таблицей (INSERT, UPDATE, DELETE).** Триггер `BEFORE UPDATE … FOR EACH ROW` получает новую версию строки `NEW`, может её изменить и должен вернуть.

> [!tip] Аналогия
> Правило для кладовщика: при любой правке накладной ставь штамп времени.

**У нас:** `NEW.updated_at := clock_timestamp()` чинит «забытый `updated_at`» операции `recategorize`, но не удаления и не долгие транзакции (лаба 04.3).

Связано: [курсор](incremental-cursor.md) · [транзакция](transaction.md)
