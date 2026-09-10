from types import SimpleNamespace

from app import metrics as metrics_module


def test_collected_metrics_have_expected_ranges(monkeypatch):
    monkeypatch.setattr(
        metrics_module.psutil,
        "virtual_memory",
        lambda: SimpleNamespace(percent=40.0),
    )
    monkeypatch.setattr(
        metrics_module.psutil,
        "disk_usage",
        lambda _: SimpleNamespace(percent=30.0),
    )
    monkeypatch.setattr(
        metrics_module.psutil,
        "net_io_counters",
        lambda: SimpleNamespace(bytes_sent=200, bytes_recv=300),
    )
    monkeypatch.setattr(metrics_module.psutil, "cpu_percent", lambda interval: 12.5)
    monkeypatch.setattr(metrics_module.psutil, "boot_time", lambda: 50)
    monkeypatch.setattr(metrics_module.time, "time", lambda: 150)

    metrics = metrics_module.collect_metrics()

    assert 0 <= metrics["cpu_percent"] <= 100
    assert 0 <= metrics["memory_percent"] <= 100
    assert 0 <= metrics["disk_percent"] <= 100
    assert metrics["uptime_seconds"] >= 0
    assert metrics["network_bytes_sent"] >= 0
    assert metrics["network_bytes_received"] >= 0
