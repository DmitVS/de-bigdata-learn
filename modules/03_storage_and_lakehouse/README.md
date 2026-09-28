# Модуль 03 · Форматы хранения и Lakehouse

**Длительность:** ~1–2 нед. · **Статус и DoD:** см. [ROADMAP](../../ROADMAP.md)

## Бизнес-вопрос

> Как хранить почасовую историю продаж 898 магазинов дёшево, надёжно и с быстрыми запросами?

## Цели

- понимать устройство Parquet
- работать с Iceberg через REST-каталог
- выбирать партиционирование осознанно

## Темы

- строчные vs колоночные форматы; Parquet: row groups, страницы, статистики, кодирование
- Apache Arrow / PyArrow как общий формат в памяти
- Iceberg: metadata → manifest list → manifests → data files; snapshots, time travel
- schema evolution, hidden partitioning, compaction, expire snapshots
- Iceberg vs Delta vs Hudi; зачем REST-каталог (Lakekeeper)
- партиционирование vs сортировка/кластеризация (sort order): pruning по партициям и по min/max статистикам; «платишь за прочитанные байты»
- совместимость схем назад и вперёд: какие изменения безопасны

## Инструменты

PyArrow, PyIceberg, DuckDB iceberg, Silo (S3), Lakekeeper

## Лабы

Каждая лаба — папка `labs/<номер>_<название>/` с README по [шаблону](../../templates/lab_README.md).

- [ ] 03.1 — PyArrow: разобрать метаданные Parquet датасета
- [ ] 03.2 — CSV vs Parquet (snappy/zstd): размер и скорость
- [ ] 03.3 — Iceberg: create/append/overwrite, snapshots, time travel, schema evolution
- [ ] 03.4 — 116 млн почасовых строк: партиционирование по дню/городу и sort order, замеры времени, прочитанных файлов и байт

## Мини-проект (вклад в capstone)

Bronze-слой FreshRetail в Iceberg (`lakehouse.bronze.*`), читается из DuckDB.

## Ресурсы

- [Surfalytics: Apache Iceberg intro](https://github.com/surfalytics/data-projects/tree/main/de-projects/15_apache_iceberg_intro)
- [Surfalytics: PyArrow intro](https://github.com/surfalytics/data-projects/tree/main/de-projects/13_pyarrow_intro)
- [Iceberg spec](https://iceberg.apache.org/spec/)
- [Lakekeeper docs](https://docs.lakekeeper.io/)

## Книга и видео

Полная таблица с пояснениями, зачем читать и что пропустить — в [карте чтения](../../reading_map.md#03--форматы-хранения-и-lakehouse).

- 📖 Клеппман, гл. 3 — столбцовое хранение
- 📖 Клеппман, гл. 4 — кодирование и эволюция схем
- 🎬 [Zoomcamp `03-data-warehouse`](https://github.com/DataTalksClub/data-engineering-zoomcamp/tree/main/03-data-warehouse) — партиционирование и кластеризация

## Домашка-чекпоинт

После всех лаб — `homework.md` по [шаблону](../../templates/homework.md).

## Заметки

Конспект, тезисы по книге и выводы — в [`notes.md`](notes.md).
