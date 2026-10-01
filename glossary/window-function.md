---
type: term
aliases: [Оконная функция, window function, OVER, QUALIFY, рамка окна]
tags: [sql]
---

# Оконная функция

**Считает значение по набору строк, связанных с текущей, и пишет его в эту же строку — число строк
не меняется** (в отличие от `GROUP BY`).

`f(x) OVER (PARTITION BY … ORDER BY … рамка)`:
- `PARTITION BY` — независимые группы;
- `ORDER BY` — порядок внутри группы;
- рамка — `ROWS` (строки) или `RANGE` (значения). По умолчанию с `ORDER BY` —
  `RANGE UNBOUNDED PRECEDING … CURRENT ROW`.

> [!tip] Аналогия
> Линейка у каждой строки ленты: видно соседей, строка на месте.

**Шаблоны:** `lag` (к прошлому), накопительный `sum … ROWS UNBOUNDED PRECEDING`, скользящее
`avg … ROWS BETWEEN 6 PRECEDING AND CURRENT ROW`, топ-N через `QUALIFY row_number() … <= N`.

**Ловушки:** `last_value` с рамкой по умолчанию = текущая строка; `RANGE` на повторах ключа.

Связано: [grain](grain.md)
