from fastapi.testclient import TestClient

from app.main import app


FAKE_METRICS = {
    "recorded_at": "2026-09-09T00:00:00+00:00",
    "cpu_percent": 12.5,
    "memory_percent": 40.0,
    "disk_percent": 30.0,
    "uptime_seconds": 100,
    "network_bytes_sent": 200,
    "network_bytes_received": 300,
}


def test_health_and_current_metrics(monkeypatch, tmp_path):
    from app import main

    test_repository = main.MetricsRepository(str(tmp_path / "api.db"), max_records=100)
    monkeypatch.setattr(main, "repository", test_repository)
    monkeypatch.setattr(main, "collect_metrics", lambda: FAKE_METRICS)

    with TestClient(app) as client:
        health_response = client.get("/api/health")
        metrics_response = client.get("/api/metrics/current")

    assert health_response.status_code == 200
    assert health_response.json() == {"status": "healthy"}
    assert metrics_response.status_code == 200
    assert "cpu_percent" in metrics_response.json()


def test_history_limit_validation(monkeypatch, tmp_path):
    from app import main

    test_repository = main.MetricsRepository(str(tmp_path / "history.db"), max_records=100)
    monkeypatch.setattr(main, "repository", test_repository)

    with TestClient(app) as client:
        response = client.get("/api/metrics/history?limit=0")

    assert response.status_code == 422


def test_prometheus_metrics_endpoint(monkeypatch, tmp_path):
    from app import main

    test_repository = main.MetricsRepository(str(tmp_path / "prometheus.db"), max_records=100)
    monkeypatch.setattr(main, "repository", test_repository)
    monkeypatch.setattr(main, "collect_metrics", lambda: FAKE_METRICS)

    with TestClient(app) as client:
        response = client.get("/metrics")

    assert response.status_code == 200
    assert "text/plain" in response.headers["content-type"]
    assert "serverscope_cpu_usage_percent" in response.text
