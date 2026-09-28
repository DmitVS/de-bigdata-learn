---
name: obsidian
description: Учебные материалы читаются в Obsidian — хранилищем служит сама папка проекта
metadata:
  type: decision
---

# Obsidian как интерфейс к материалам курса

**Решение (2026-09-28).** Папка `DE_BigData_Learn/` открывается в Obsidian как отдельное хранилище
(vault). Материалы остаются обычными `.md` в git: их одинаково читают Obsidian, VS Code, GitHub и
AI-ассистенты.

**Почему не отдельное хранилище / копия.** Один источник правды: без синхронизации и расхождений.
Существующее хранилище `~/ObsidianVault` (Hermes Skills) к курсу не относится.

**Не нарушает [«только контейнеры»](containers-only.md):** Obsidian уже был установлен на хосте
(snap) и только читает файлы, в стек не входит. Плагины сообщества ставятся `make obsidian` в
одноразовом контейнере `curlimages/curl`, версии зафиксированы в `scripts/obsidian_plugins.sh`.

**Конвенции:**
- Ссылки — markdown, относительные пути (`useMarkdownLinks`), без `[[wikilinks]]`: так они работают
  и на GitHub, и в VS Code.
- Врезки — callouts `> [!tip]`, `> [!warning]` и т.д.; ответы — сворачиваемые `> [!success]-`.
- Плагины: Spaced Repetition 1.15.4 (карточки `flashcards.md`), Excalidraw 2.27.3 (рисунки в
  `maps/` модуля, без сжатия — читаемые диффы), Advanced Tables 0.23.2 (редактирование таблиц).
- Folder Notes 1.8.26: клик по папке модуля открывает её `README.md` (хаб модуля).
- Встроенные: Canvas (карты в `modules/NN_*/maps/`), Bases, Graph, Page preview (всплывающие термины).
- Структура (2026-09-28): всё, что относится к модулю, — в его папке (`theory/`, `labs/`, `maps/`,
  `flashcards.md`, `cheatsheet.md`, `homework.md`, `notes.md`); в корне — только общее для курса
  (`glossary/`, `reading_map.md`, `ROADMAP.md`, `capstone/`, `infra/`…).
- В git: `.obsidian/app.json`, `core-plugins.json`, `community-plugins.json`, `graph.json`,
  `templates.json`, `plugins/*/data.json`. Не в git: `workspace*.json`, код плагинов.
