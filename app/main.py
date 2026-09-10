import asyncio
from contextlib import asynccontextmanager, suppress

from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse, Response
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from app.config import settings
from app.database import MetricsRepository
from app.metrics import collect_metrics
from app.observability import update_prometheus_metrics


repository = MetricsRepository(settings.db_path)


def collect_and_record() -> dict:
    metrics = collect_metrics()
    update_prometheus_metrics(metrics)
    return repository.save(metrics)


async def collection_loop() -> None:
    while True:
        collect_and_record()
        await asyncio.sleep(settings.collection_interval)


@asynccontextmanager
async def lifespan(_: FastAPI):
    repository.initialize()
    task = asyncio.create_task(collection_loop())
    yield
    task.cancel()
    with suppress(asyncio.CancelledError):
        await task


app = FastAPI(
    title="ServerScope",
    description="A lightweight server health monitoring API.",
    version="0.1.0",
    lifespan=lifespan,
)


@app.get("/", response_class=HTMLResponse)
def dashboard() -> str:
    return """
    <!doctype html>
    <html lang="en">
      <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>ServerScope</title>
        <style>
          body { font-family: system-ui, sans-serif; max-width: 900px; margin: 3rem auto;
                 padding: 0 1rem; background: #0b1220; color: #e5e7eb; }
          h1 { color: #60a5fa; } .grid { display: grid; gap: 1rem;
          grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); }
          .card { background: #172033; border: 1px solid #293750; border-radius: 12px;
                  padding: 1.25rem; } .value { font-size: 2rem; font-weight: 700; }
          a { color: #93c5fd; }
        </style>
      </head>
      <body>
        <h1>ServerScope</h1>
        <p>Live health metrics for this server.</p>
        <div class="grid">
          <div class="card">CPU<div class="value" id="cpu">--</div></div>
          <div class="card">Memory<div class="value" id="memory">--</div></div>
          <div class="card">Disk<div class="value" id="disk">--</div></div>
          <div class="card">Uptime<div class="value" id="uptime">--</div></div>
        </div>
        <p><a href="/docs">Open API documentation</a></p>
        <script>
          async function refresh() {
            const m = await fetch('/api/metrics/current').then(r => r.json());
            document.querySelector('#cpu').textContent = m.cpu_percent + '%';
            document.querySelector('#memory').textContent = m.memory_percent + '%';
            document.querySelector('#disk').textContent = m.disk_percent + '%';
            document.querySelector('#uptime').textContent = Math.floor(m.uptime_seconds / 3600) + 'h';
          }
          refresh(); setInterval(refresh, 15000);
        </script>
      </body>
    </html>
    """


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "healthy" if repository.is_healthy() else "unhealthy"}


@app.get("/api/metrics/current")
def current_metrics() -> dict:
    return collect_and_record()


@app.get("/api/metrics/history")
def metric_history(limit: int = Query(default=100, ge=1, le=1000)) -> list[dict]:
    return repository.recent(limit)


@app.get("/metrics", include_in_schema=False)
def prometheus_metrics() -> Response:
    collect_and_record()
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
