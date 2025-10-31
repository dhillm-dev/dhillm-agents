# Global Agents — Render Setup

## Deploy (one-click via render.yaml)
1. Push this repo to GitHub.
2. On `https://render.com` → New + → "Blueprint" → select this repo (render.yaml).
3. Render creates:
   - Web: `global-agents-api` (FastAPI)
   - Worker: `global-agents-worker` (looper)
4. Wait for both to turn green.

## Endpoints
- `GET  /api/healthz`          → `{ok:true}`
- `POST /api/run_once`         → `{ok:true, decision:{...}}`
- `GET  /api/last_decision`
- `GET  /api/correl_scan`

## Env Vars
- `API_BASE` (worker points to web URL)
- `UNIVERSE` (comma list)
- `TF`, `COOLDOWN`, `HTTP_TIMEOUT`
- `REDIS_URL` (optional; persists last_decision)

## Local dev
```bash
pip install -r requirements.txt
uvicorn api.healthz:app --host 0.0.0.0 --port 8000
python -m global_agents.worker.looper
```

## Smoke test (PowerShell)
See `tests/run_render.ps1`.# dhillm-agents
