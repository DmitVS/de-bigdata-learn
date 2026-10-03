---
type: term
aliases: [Terraform, IaC, инфраструктура как код, провайдер, state, backend, plan, apply, import, дрейф]
tags: [dataops, infra]
---

# Terraform

**Декларативная инфраструктура как код.** В HCL описывают, какими должны быть ресурсы;
провайдер (плагин) знает API системы; `plan` сравнивает код, **state** (что Terraform создал, с
ID) и реальность; `apply` доводит реальность до кода. State держат в удалённом backend с
блокировкой; ресурс, созданный руками, берут под управление `import`.

> [!tip] Аналогия
> Смета (код), журнал прораба (state) и прораб, который доводит стройку до сметы (apply).

**У нас:** `hashicorp/terraform:1.16.5` в контейнере, `make tf ARGS="…"`; провайдеры
`aminueza/minio` (Silo) и `cyrilgdn/postgresql`; state — `s3://tfstate/local-stack/terraform.tfstate`
в Silo с `use_lockfile`. Цикл: 4 to add → Apply complete → No changes → Destroy complete.

Связано: [DataOps](dataops.md) · [S3](s3.md)
