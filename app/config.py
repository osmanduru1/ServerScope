import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    db_path: str = os.getenv("SERVERSCOPE_DB_PATH", "data/serverscope.db")
    collection_interval: int = int(
        os.getenv("SERVERSCOPE_COLLECTION_INTERVAL", "15")
    )
    max_metric_records: int = int(os.getenv("SERVERSCOPE_MAX_METRIC_RECORDS", "10000"))


settings = Settings()
