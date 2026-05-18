# Flask QPS-limited demo

## Endpoints

- `GET /biz`
  - Sleeps tens of milliseconds (default `SLEEP_MS=30`).
  - Rejects when last-1s hits reach `QPS_LIMIT` (default 150), returns `429` JSON.
- `GET /healthz`
  - Returns JSON including sliding count of `/biz` hits in the last 10 seconds.

## Run locally

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
$env:PORT=8080
python app.py
```

## Build & run with Docker

```powershell
docker build -t flask-qps-demo .
docker run --rm -p 8080:8080 flask-qps-demo
```

## GitHub Actions

Workflow builds Docker image on PRs, and builds + pushes to GHCR on `main`.
