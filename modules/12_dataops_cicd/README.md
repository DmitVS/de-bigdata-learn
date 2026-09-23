# Модуль 12 · DataOps и CI/CD

**Длительность:** ~1 нед. · **Статус и DoD:** см. [ROADMAP](../../ROADMAP.md)

## Бизнес-вопрос

> Как менять pipeline часто и без страха что-то сломать?

## Цели

- автоматизировать проверки
- настроить CI для dbt
- понимать IaC и метрики DataOps

## Темы

- pre-commit, линтеры (ruff, sqlfmt, yamllint)
- GitHub Actions: lint → test → `dbt build` на выборке (slim CI)
- окружения dev/prod, секреты в CI
- Terraform: как этот стек выглядел бы в облаке
- DORA, SLA/SLO/SLI, MTTD/MTTR, TCO

## Инструменты

GitHub Actions, pre-commit, Terraform (обзор)

## Лабы

Каждая лаба — папка `labs/<номер>_<название>/` с README по [шаблону](../../templates/lab_README.md).

- [ ] 12.1 — pre-commit (в контейнере)
- [ ] 12.2 — CI в GitHub Actions
- [ ] 12.3 — Terraform: S3-бакет и Postgres у облачного провайдера (plan без apply)

## Мини-проект (вклад в capstone)

Каждый PR проходит lint + тесты + dbt build автоматически.

## Ресурсы

- [Surfalytics: Git and CI/CD](https://github.com/surfalytics/data-projects/tree/main/dataops-projects/01_git_and_ci_cd)
- [Surfalytics: Terraform 101](https://github.com/surfalytics/data-projects/tree/main/dataops-projects/02_terraform_101)

## Заметки

Конспект и выводы — в [`notes.md`](notes.md).
