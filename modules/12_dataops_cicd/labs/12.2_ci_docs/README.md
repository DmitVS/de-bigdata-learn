# Лаба 12.2 · CI в GitHub Actions и документация на GitHub Pages

**Модуль:** [12 · DataOps и CI/CD](../../README.md) · **Дата начала:** YYYY-MM-DD · **Статус:** ⬜

## Objective

Каждый pull request в репозиторий курса автоматически проходит lint, тесты и сборку dbt; сборка
dbt — только изменённых моделей (slim CI). После мержа документация dbt публикуется на GitHub
Pages и всегда соответствует коду. Это мини-проект модуля: вклад в критерии 2 и 7 рубрики
capstone.

## Key Terms

_(заполни своими словами)_

- **Workflow, job, step, runner, action** —
- **Секреты и права (`permissions`) в Actions** —
- **Slim CI: `state:modified+`, `--defer`, `--state`** —
- **Артефакт, GitHub Pages** —

## Prerequisites

- Лаба 12.1: курс в отдельном репозитории
- Теория: [03 · GitHub Actions](../../theory/03_github_actions.md), [04 · Документация как артефакт](../../theory/04_docs_artifact.md)
- Образец: `.github/workflows/ci.yml`, `scripts/ci/*.sh`, `make ci`

## Tasks

### Task 1. CI проходит локально и на GitHub

**Expected result / Definition of Done:**
- `make ci` проходит локально; время каждого шага — в README
- Тот же workflow зелёный на GitHub на pull request; ссылка на запуск — в README
- Намеренная ошибка (тест или dbt-тест) делает CI красным; pull request с ней нельзя смержить
  (правило защиты ветки `main`: обязательные проверки)

**Steps:**
1. Включи Actions в репозитории и защиту ветки `main` (Settings → Branches).
2. Открой pull request с безобидным изменением, затем с намеренной ошибкой.

### Task 2. dbt-проект capstone в CI

**Expected result / Definition of Done:**
- Шаг dbt собирает **проект capstone** (а не только учебный модуля 05) на данных, которые CI
  получает сам (датасет с Hugging Face или выборка), без нашего стека
- Slim CI работает: на pull request, меняющем одну модель, собираются только она и её потомки —
  список из лога CI в README
- В README — что делает `--defer` и что случится на первом pull request, когда состояния прода ещё
  нет

**Steps:**
1. Определи, какой цели dbt (target) нужно в CI и откуда она берёт данные.
2. Добавь шаг в `scripts/ci/dbt.sh` или отдельный скрипт; проверь через `make ci CI_STEPS="dbt"`.

### Task 3. Документация на Pages

**Expected result / Definition of Done:**
- После мержа в `main` сайт `dbt docs` открывается по адресу GitHub Pages; ссылка — в README
  репозитория
- На сайте — модели capstone с описаниями и граф lineage
- `manifest.json` с Pages используется как состояние прода в slim CI (видно в логе pull request)

## Результат

_(ссылки на запуски CI и на сайт документации)_

## Выводы и вопросы

- Сколько минут CI стоит один pull request? Что бы ты ускорил первым?
