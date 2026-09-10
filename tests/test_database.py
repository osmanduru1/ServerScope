from app.database import MetricsRepository


SAMPLE_METRICS = {
    "recorded_at": "2026-09-09T00:00:00+00:00",
    "cpu_percent": 12.5,
    "memory_percent": 40.0,
    "disk_percent": 30.0,
    "uptime_seconds": 100,
    "network_bytes_sent": 200,
    "network_bytes_received": 300,
}


def test_repository_saves_and_returns_metrics(tmp_path):
    repository = MetricsRepository(str(tmp_path / "test.db"))
    repository.initialize()

    saved = repository.save(SAMPLE_METRICS)
    history = repository.recent(10)

    assert saved["id"] == 1
    assert len(history) == 1
    assert history[0]["cpu_percent"] == 12.5
    assert repository.is_healthy()

