from app.metrics import collect_metrics


def test_collected_metrics_have_expected_ranges():
    metrics = collect_metrics()

    assert 0 <= metrics["cpu_percent"] <= 100
    assert 0 <= metrics["memory_percent"] <= 100
    assert 0 <= metrics["disk_percent"] <= 100
    assert metrics["uptime_seconds"] >= 0
    assert metrics["network_bytes_sent"] >= 0
    assert metrics["network_bytes_received"] >= 0

