$ErrorActionPreference = "Stop"
Write-Host "== Install =="
python -m pip install -U pip
pip install -r requirements.txt; if($LASTEXITCODE -ne 0){ Write-Host "[warn] pip install failed, continuing for smoke" }

Write-Host "== Start API (healthz only) =="
Start-Process -NoNewWindow -FilePath python -ArgumentList "-m","uvicorn","api.healthz:app","--host","0.0.0.0","--port","8000"
Start-Sleep -s 2

Write-Host "== Check health =="
Invoke-WebRequest -UseBasicParsing -Uri "http://127.0.0.1:8000/api/healthz" | Select-Object -ExpandProperty Content

Write-Host "== Run worker one pass =="
$env:API_BASE="http://127.0.0.1:8000"
$env:UNIVERSE="EURUSD=X,BTC-USD"
$env:TF="1h"
$env:COOLDOWN="5"
$env:HTTP_TIMEOUT="15"
$py = @'
import os, sys, time
sys.path.insert(0, os.getcwd())
from global_agents.worker.looper import run_once
for s in os.getenv("UNIVERSE").split(","):
    try:
        print(s, run_once(s))
    except Exception as e:
        print("ERR", s, e)
'@
$tmp = [System.IO.Path]::Combine([System.IO.Path]::GetTempPath(), "render_smoke_" + [System.Guid]::NewGuid().ToString() + ".py")
Set-Content -Path $tmp -Value $py -Encoding UTF8
python $tmp
Remove-Item $tmp -Force -ErrorAction SilentlyContinue

Write-Host "== Done =="