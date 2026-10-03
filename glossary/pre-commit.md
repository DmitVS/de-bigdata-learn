---
type: term
aliases: [pre-commit, git-хук, git hook, хук]
tags: [dataops]
---

# pre-commit

**Фреймворк git-хуков: перед коммитом запускает проверки изменённых файлов по
`.pre-commit-config.yaml`.** Хуки бывают проверяющие и чинящие (чинящий тоже возвращает ошибку —
правку надо добавить в коммит). Хуки из внешних репозиториев скачиваются в кэш; `repo: local` —
свои команды; `language: system` — инструмент из текущего окружения.

> [!tip] Аналогия
> Охранник у двери git: проверяет сумки и застёгивает расстёгнутые.

**У нас:** pre-commit в образе workspace (группа `dev`), `make precommit`, хук git —
`scripts/git-hooks/pre-commit` → `make precommit` (`make hooks`). Полный прогон по курсу — ~17 с;
ruff, sqlfmt, yamllint — `language: system` (версии из `uv.lock`); хук-запрет `.env`.

Связано: [CI/CD](ci-cd.md) · [DataOps](dataops.md)
