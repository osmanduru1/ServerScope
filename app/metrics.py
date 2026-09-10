from datetime import datetime, timezone
import time

import psutil


def collect_metrics() -> dict[str, float | int | str]:
    """Collect a point-in-time snapshot of host system health."""
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage("/")
    network = psutil.net_io_counters()

    return {
        "recorded_at": datetime.now(timezone.utc).isoformat(),
        "cpu_percent": psutil.cpu_percent(interval=0.1),
        "memory_percent": memory.percent,
        "disk_percent": disk.percent,
        "uptime_seconds": int(time.time() - psutil.boot_time()),
        "network_bytes_sent": network.bytes_sent,
        "network_bytes_received": network.bytes_recv,
    }

