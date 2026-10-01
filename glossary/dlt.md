---
type: term
aliases: [dlt, ресурс dlt, источник dlt, пайплайн dlt, load package, пакет загрузки]
tags: [ingestion, инструмент]
---

# dlt (data load tool)

**Python-библиотека загрузки данных: ты пишешь генератор, отдающий данные, а dlt выводит схему, нормализует, хранит состояние и пишет в хранилище.** Кирпичики: ресурс (`@dlt.resource`, таблица), источник (`@dlt.source`, группа ресурсов), трансформер (`|`), пайплайн (`dlt.pipeline`). Запуск — extract → normalize → load; между шагами пакет загрузки лежит на диске.

> [!tip] Аналогия
> Приёмщик склада: распаковывает посылки в стандартные коробки и ведёт журнал приёмки.

**У нас:** dlt 1.30; рабочие папки в `data/.dlt` (`DLT_DATA_DIR`), секреты из окружения (`infra/docker/core.yaml`), Iceberg через `filesystem` + `table_format="iceberg"` внутри `s3://warehouse/lakehouse/`.

Связано: [нормализация](nested-normalization.md) · [способы записи](write-disposition.md) · [курсор](incremental-cursor.md)
