"""Скачивание FreshRetailNet-50K с Hugging Face в data/raw/freshretailnet_50k/.

Запуск: `make data` (внутри контейнера workspace). Повторный запуск докачивает только
изменившиеся файлы. Загрузка в S3/Iceberg — это уже упражнения модулей 03–04.
"""

from pathlib import Path

import duckdb
from huggingface_hub import snapshot_download

REPO_ID = "Dingdong-Inc/FreshRetailNet-50K"
TARGET = Path("data/raw/freshretailnet_50k")


def main() -> None:
    path = snapshot_download(repo_id=REPO_ID, repo_type="dataset", local_dir=TARGET)
    print(f"Скачано в {path}")

    stats = duckdb.sql(
        f"""
        select
            count(*)                   as rows,
            count(distinct store_id)   as stores,
            count(distinct product_id) as skus,
            count(distinct city_id)    as cities,
            min(dt)                    as dt_from,
            max(dt)                    as dt_to
        from read_parquet('{TARGET}/data/*.parquet')
        """
    )
    stats.show()


if __name__ == "__main__":
    main()
