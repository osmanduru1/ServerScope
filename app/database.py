from pathlib import Path
import sqlite3
from typing import Any


CREATE_METRICS_TABLE = """
CREATE TABLE IF NOT EXISTS metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    recorded_at TEXT NOT NULL,
    cpu_percent REAL NOT NULL,
    memory_percent REAL NOT NULL,
    disk_percent REAL NOT NULL,
    uptime_seconds INTEGER NOT NULL,
    network_bytes_sent INTEGER NOT NULL,
    network_bytes_received INTEGER NOT NULL
)
"""

CREATE_RECORDED_AT_INDEX = """
CREATE INDEX IF NOT EXISTS idx_metrics_recorded_at ON metrics(recorded_at)
"""


class MetricsRepository:
    def __init__(self, db_path: str, max_records: int = 10000):
        self.db_path = db_path
        self.max_records = max_records

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.db_path, timeout=10)
        connection.row_factory = sqlite3.Row
        return connection

    def initialize(self) -> None:
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as connection:
            connection.execute("PRAGMA journal_mode=WAL")
            connection.execute("PRAGMA busy_timeout=10000")
            connection.execute(CREATE_METRICS_TABLE)
            connection.execute(CREATE_RECORDED_AT_INDEX)

    def save(self, metrics: dict[str, Any]) -> dict[str, Any]:
        with self._connect() as connection:
            cursor = connection.execute(
                """
                INSERT INTO metrics (
                    recorded_at, cpu_percent, memory_percent, disk_percent,
                    uptime_seconds, network_bytes_sent, network_bytes_received
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    metrics["recorded_at"],
                    metrics["cpu_percent"],
                    metrics["memory_percent"],
                    metrics["disk_percent"],
                    metrics["uptime_seconds"],
                    metrics["network_bytes_sent"],
                    metrics["network_bytes_received"],
                ),
            )
            self._enforce_retention(connection)
        return {"id": cursor.lastrowid, **metrics}

    def recent(self, limit: int) -> list[dict[str, Any]]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT * FROM metrics ORDER BY id DESC LIMIT ?", (limit,)
            ).fetchall()
        return [dict(row) for row in rows]

    def is_healthy(self) -> bool:
        try:
            with self._connect() as connection:
                connection.execute("SELECT 1").fetchone()
            return True
        except sqlite3.Error:
            return False

    def _enforce_retention(self, connection: sqlite3.Connection) -> None:
        if self.max_records <= 0:
            return
        connection.execute(
            """
            DELETE FROM metrics
            WHERE id NOT IN (
                SELECT id FROM metrics ORDER BY id DESC LIMIT ?
            )
            """,
            (self.max_records,),
        )
