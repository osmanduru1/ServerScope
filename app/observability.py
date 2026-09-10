from collections.abc import Mapping

from prometheus_client import Gauge


CPU_PERCENT = Gauge(
    "serverscope_cpu_usage_percent",
    "Current CPU utilization as a percentage.",
)
MEMORY_PERCENT = Gauge(
    "serverscope_memory_usage_percent",
    "Current memory utilization as a percentage.",
)
DISK_PERCENT = Gauge(
    "serverscope_disk_usage_percent",
    "Current root filesystem utilization as a percentage.",
)
UPTIME_SECONDS = Gauge(
    "serverscope_uptime_seconds",
    "Host uptime in seconds.",
)
NETWORK_BYTES_SENT = Gauge(
    "serverscope_network_bytes_sent_total",
    "Total bytes sent by the host since boot.",
)
NETWORK_BYTES_RECEIVED = Gauge(
    "serverscope_network_bytes_received_total",
    "Total bytes received by the host since boot.",
)


def update_prometheus_metrics(metrics: Mapping[str, float | int | str]) -> None:
    """Update Prometheus gauges from a ServerScope host snapshot."""
    CPU_PERCENT.set(float(metrics["cpu_percent"]))
    MEMORY_PERCENT.set(float(metrics["memory_percent"]))
    DISK_PERCENT.set(float(metrics["disk_percent"]))
    UPTIME_SECONDS.set(float(metrics["uptime_seconds"]))
    NETWORK_BYTES_SENT.set(float(metrics["network_bytes_sent"]))
    NETWORK_BYTES_RECEIVED.set(float(metrics["network_bytes_received"]))

