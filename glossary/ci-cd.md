---
type: term
aliases: [CI, CD, CI/CD, GitHub Actions, workflow, job, runner, slim CI, state:modified, defer]
tags: [dataops]
---

# CI/CD и slim CI

**CI — автоматическая проверка каждого изменения (lint, тесты, сборка); CD — автоматическая
выкатка проверенного.** В GitHub Actions workflow (YAML в `.github/workflows/`) состоит из jobs на
раннерах, job — из steps (команды и готовые actions). **Slim CI** в dbt собирает только изменённые
модели и их потомков (`--select state:modified+`), а непересобранные берёт из прода
(`--defer --state <manifest прода>`).

> [!tip] Аналогия
> Контроль качества на каждой детали и автоматическая отгрузка годных.

**У нас:** `.github/workflows/ci.yml` (для отдельного репозитория курса), шаги — `scripts/ci/*.sh`,
локально — `make ci` в чистом контейнере uv без стека; состояние прода — `manifest.json` с GitHub Pages.

Связано: [DataOps](dataops.md) · [pre-commit](pre-commit.md) · [документация как код](docs-as-code.md)
