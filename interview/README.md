# Собеседования и рынок

Начинаем рано (с фазы 2): собеседования быстрее всего показывают пробелы.

| Папка / файл | Что |
|---|---|
| `market.md` | обзор вакансий: частотность навыков (модуль 01) |
| `take-home/` | тестовые задания: условие, решение на своём стеке, разбор |
| `mock/` | mock-интервью по сценариям: SQL-рефакторинг, моделирование, dbt, system design |
| `questions.md` | банк вопросов на повторение из `notes.md` модулей |

## Формат mock-интервью (по мотивам Surfalytics AE mock interview)

1. Разобрать и отрефакторить чужой SQL, `UNION` vs `UNION ALL`, дедупликация, оптимизация.
2. Спроектировать модель данных под медленный дашборд.
3. dbt: слои, материализации и trade-offs, стратегия тестов, как ускорить dev на 14 млрд строк.
4. Процесс: размер PR, деплой, мониторинг после релиза.
5. System design: pipeline для сети из 900 магазинов (батч + near-real-time).

Источники: [Surfalytics mock AE interview](https://github.com/surfalytics/data-projects/tree/main/ae-projects/01_mock_ae_interview),
[Data-Learn interview-tests](https://github.com/Data-Learn/data-engineering/tree/master/interview-tests).
