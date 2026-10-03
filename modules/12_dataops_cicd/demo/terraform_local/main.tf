# Учебная инфраструктура как код (модуль 12): Terraform управляет ресурсами нашего же стека.
#   - бакет exports в Silo (S3) + политика «только чтение» для выгрузок партнёрам;
#   - роль reporting и база reporting в Postgres.
# Провайдеры: aminueza/minio (Silo совместим с MinIO API), cyrilgdn/postgresql.
# Запуск: make tf ARGS="init" → make tf ARGS="plan" → make tf ARGS="apply"
terraform {
  required_version = ">= 1.16"

  # Состояние — в бакете tfstate нашего Silo, а не файлом рядом с кодом: его видят все запуски
  # (ноутбук, CI), а use_lockfile не даёт двум apply менять инфраструктуру одновременно.
  # Ключи доступа — переменные окружения AWS_ACCESS_KEY_ID / AWS_SECRET_ACCESS_KEY.
  backend "s3" {
    bucket                      = "tfstate"
    key                         = "local-stack/terraform.tfstate"
    region                      = "local-01"
    endpoints                   = { s3 = "http://silo:9000" }
    use_path_style              = true
    use_lockfile                = true
    skip_credentials_validation = true
    skip_region_validation      = true
    skip_requesting_account_id  = true
    skip_metadata_api_check     = true
    skip_s3_checksum            = true
  }

  required_providers {
    minio = {
      source  = "aminueza/minio"
      version = "~> 3.0"
    }
    postgresql = {
      source  = "cyrilgdn/postgresql"
      version = "~> 1.25"
    }
  }
}

variable "s3_user" { type = string }
variable "s3_password" {
  type      = string
  sensitive = true
}
variable "pg_user" { type = string }
variable "pg_password" {
  type      = string
  sensitive = true
}

provider "minio" {
  minio_server   = "silo:9000"
  minio_user     = var.s3_user
  minio_password = var.s3_password
  minio_region   = "local-01"
}

provider "postgresql" {
  host     = "postgres"
  port     = 5432
  username = var.pg_user
  password = var.pg_password
  sslmode  = "disable"
}

resource "minio_s3_bucket" "exports" {
  bucket = "exports"
}

resource "minio_s3_bucket_versioning" "exports" {
  bucket = minio_s3_bucket.exports.bucket
  versioning_configuration {
    status = "Enabled"
  }
}

resource "postgresql_role" "reporting" {
  name  = "reporting"
  login = false
}

resource "postgresql_database" "reporting" {
  name  = "reporting"
  owner = postgresql_role.reporting.name
}

output "bucket" {
  value = minio_s3_bucket.exports.bucket
}
