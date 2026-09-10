# ServerScope

ServerScope is a containerized single-host Linux monitoring service. It collects
system health metrics, stores bounded historical readings, exposes REST and
Prometheus-compatible endpoints, and visualizes time-series data through a
provisioned Grafana dashboard.

## Current MVP

- CPU, memory, disk, uptime, and network I/O monitoring
- SQLite-backed metric history
- Configurable background collection interval
- Bounded local retention to prevent unbounded SQLite growth
- Resilient background collection loop with error logging
- JSON API for current and historical metrics
- Prometheus-compatible metrics endpoint
- Prometheus time-series collection
- Automatically provisioned Grafana data source and dashboard
- Health endpoint for container and deployment checks
- Docker and Docker Compose support
- Automated tests

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open <http://localhost:8000> for the lightweight dashboard or
<http://localhost:8000/docs> for the interactive API documentation. This mode
does not launch Prometheus or Grafana.

## Run with Docker

```bash
docker compose up --build
```

Metrics are persisted in the `serverscope-data` Docker volume.

After the stack starts:

- ServerScope: <http://localhost:8000>
- Prometheus: <http://localhost:9090>
- Grafana: <http://localhost:3000>

Sign into Grafana with `admin` / `admin`, then open **Dashboards → ServerScope →
ServerScope Overview**. Change this development password before exposing Grafana
outside your local machine.

## Configuration

| Variable | Default | Purpose |
| --- | --- | --- |
| `SERVERSCOPE_DB_PATH` | `data/serverscope.db` | SQLite database path |
| `SERVERSCOPE_COLLECTION_INTERVAL` | `15` | Seconds between readings |
| `SERVERSCOPE_MAX_METRIC_RECORDS` | `10000` | Maximum readings retained locally |
| `GRAFANA_ADMIN_USER` | `admin` | Grafana development admin user |
| `GRAFANA_ADMIN_PASSWORD` | `admin` | Grafana development admin password |

Set a non-default Grafana password before exposing the stack outside a local
development network.

## API

- `GET /api/health` — service and database status
- `GET /api/metrics/current` — collect and return a current reading
- `GET /api/metrics/history?limit=100` — return recent readings
- `GET /metrics` — expose the latest host metrics in Prometheus format

## Planned milestones

1. Configurable Prometheus alert rules and alert history
2. Multi-server agents with authenticated ingestion
3. PostgreSQL storage
4. Email or webhook notifications
5. Deployment documentation and observability for ServerScope itself
