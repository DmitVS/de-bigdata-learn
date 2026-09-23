# Модуль 00 · Just enough: CLI, Git, Docker, Make

**Длительность:** ~1 нед. · **Статус и DoD:** см. [ROADMAP](../../ROADMAP.md)

## Бизнес-вопрос

> Как за одну команду поднять воспроизводимое рабочее окружение, в котором будет жить весь курс?

## Цели

- уверенно работать в терминале, git и docker compose
- понимать каждый сервис слоя core и уметь его диагностировать
- скачать датасет и убедиться, что он соответствует описанию

## Темы

- CLI: навигация, пайпы, grep/sed/jq, права, процессы
- Git: ветки, коммиты, PR, .gitignore, секреты вне git
- Docker: образ vs контейнер, слои, тома, сети, healthcheck; Compose: include, profiles, depends_on
- Makefile как единая точка входа; uv и lock-файлы (внутри контейнера)
- S3-модель хранения: бакеты, ключи, path-style; зачем Iceberg REST-каталог

## Инструменты

Docker Compose, Make, git, Silo (S3), Postgres, Lakekeeper, контейнер workspace

## Лабы

Каждая лаба — папка `labs/<номер>_<название>/` с README по [шаблону](../../templates/lab_README.md).

- [ ] 00.1 — разбор `infra/docker/core.yaml`: схема сервисов, портов и томов
- [ ] 00.2 — `make up` / `make check` / `make logs`: сломать и починить (неверный пароль в .env, занятый порт)
- [ ] 00.3 — `make data`: скачать FreshRetailNet-50K и проверить статистику в DuckDB CLI

## Мини-проект (вклад в capstone)

Шпаргалка `cheatsheets/docker-compose.md` + заметка «как устроено моё окружение».

## Ресурсы

- [Surfalytics: just enough CLI / Git / Docker](https://github.com/surfalytics/analytics-course/tree/main/00_prerequisites)
- [Data-Learn: How to get git](https://github.com/Data-Learn/data-engineering/blob/master/how-to/How%20to%20get%20git.md)
- [Docker Compose docs](https://docs.docker.com/compose/)

## Заметки

Конспект и выводы — в [`notes.md`](notes.md).
