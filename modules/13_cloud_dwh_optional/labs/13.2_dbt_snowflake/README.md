# Лаба 13.2 · dbt-проект capstone на Snowflake

**Модуль:** [13 · Облачное хранилище](../../README.md) · **Дата начала:** YYYY-MM-DD · **Статус:** ⬜

## Objective

Собрать dbt-проект capstone (или его часть до витрин) в Snowflake и получить те же числа, что в
lakehouse. Понять, какие места проекта зависят от хранилища.

## Key Terms

_(заполни своими словами)_

- **Адаптер dbt, цель (target)** —
- **Различия диалектов** —

## Prerequisites

- Лаба 13.1: `raw.sales` загружена
- Теория: [02 · Загрузка и dbt](../../theory/02_load_and_dbt.md)
- Образец: `demo/dbt_snowflake/`

## Tasks

### Task 1. Цель snowflake в проекте capstone

**Expected result / Definition of Done:**
- В профиле capstone — цель `snowflake` с реквизитами из окружения; `dbt debug --target snowflake`
  успешен
- `dbt parse --target snowflake` проходит и без реквизитов (объясни почему)

### Task 2. Перенос моделей

**Expected result / Definition of Done:**
- `dbt build --target snowflake` зелёный: модели и тесты; список правок, которые понадобились, с
  причиной каждой (диалект, имена, материализации)
- Одна витрина сверена с lakehouse на трёх разрезах (числа в README)
- Время сборки и потраченные кредиты — в README

### Task 3. Возможности Snowflake

**Expected result / Definition of Done:**
- Dev-окружение как `CREATE DATABASE … CLONE` прода; сколько места заняла копия сразу после
  создания (объясни)
- Time travel: витрина «час назад» после намеренной порчи данных; восстановление

## Результат

_(правки, сверка, время и кредиты)_

## Выводы и вопросы

- Какие модели capstone ты бы держал в Snowflake, а какие — в lakehouse, если бы использовал оба?
