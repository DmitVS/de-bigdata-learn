---
name: dataset
description: Основной датасет курса — FreshRetailNet-50K; критерии выбора и отброшенные альтернативы
metadata:
  type: decision
---

Решение от 2026-09-23: основной датасет — **FreshRetailNet-50K** (Dingdong, 898 магазинов,
863 SKU, почасовые продажи/остатки/промо/погода, 2024-03-28…2024-06-07, CC-BY-4.0).

Критерии пользователя: розничная **сеть**, **≥100 торговых точек**, **≥100 SKU**.

Отброшены:
- Favorita (54 магазина), M5/Walmart (10), Predict Future Sales (60), Walmart Recruiting (45, отделы) — мало магазинов.
- Rossmann — 1 115 магазинов, но без SKU.
- Synthetic U.S. E-Commerce 1M (Kaggle) — маркетплейс без магазинов, синтетика по мотивам Olist.
- Dominick's, dunnhumby Complete Journey, X5 Retail Hero, Iowa Liquor — подходят частично, оставлены как резерв.

Минусы FreshRetail (короткий период, анонимные ID, нет цен) закрываем учебной OLTP-базой
`retail_oltp` с генератором изменений (SCD2, CDC) и синтетическим масштабированием ×10.
