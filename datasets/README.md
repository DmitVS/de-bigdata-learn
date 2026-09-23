# Датасеты

## FreshRetailNet-50K (основной)

- Источник: [Hugging Face — Dingdong-Inc/FreshRetailNet-50K](https://huggingface.co/datasets/Dingdong-Inc/FreshRetailNet-50K),
  статья [arXiv:2505.16319](https://arxiv.org/abs/2505.16319). Лицензия **CC-BY-4.0**.
- Сеть Dingdong (свежие продукты): **898 магазинов, 18 городов, 863 SKU**, 50 000 рядов магазин×товар.
- Файлы: `data/train.parquet` (~106 МБ), `data/eval.parquet` (~8 МБ).
- **Факт по `make data` (2026-09-23):** 4 850 000 строк · 898 магазинов · **865** `product_id` · 18 городов · 2024-03-28 — **2024-07-02**.
  Описание датасета говорит о 863 SKU и периоде до 2024-06-07 — разобрать расхождения в лабе 00.3.
- Скачать: `make data` → `data/raw/freshretailnet_50k/` (вне git).

| Группа | Колонки |
|---|---|
| Иерархия | `city_id`, `store_id`, `management_group_id`, `first/second/third_category_id`, `product_id` |
| Время | `dt` |
| Продажи | `sale_amount`, `hours_sale` (массив 24 значений) |
| Наличие | `stock_hour6_22_cnt`, `hours_stock_status` (массив 24 флагов) |
| Промо | `discount`, `holiday_flag`, `activity_flag` |
| Погода | `precpt`, `avg_temperature`, `avg_humidity`, `avg_wind_level` |

Особенности: все ID анонимизированы, нет названий и цен (только скидка). Разворот почасовых
массивов даёт ~116 млн строк — основной объём для модулей 03 и 07.

## Дополнительные источники (по мере курса)

- **retail_oltp** (Postgres) — справочники сети, сгенерированные из FreshRetail, + генератор изменений → SCD2 и CDC (модули 04, 05, 08).
- **Публичный API** — для лабы по загрузке из API (модуль 04).
- **Синтетическое масштабирование ×10** — для нагрузочных сравнений (модуль 07).

Почему этот датасет и что отбросили — [`memory/decisions/dataset.md`](../memory/decisions/dataset.md).
