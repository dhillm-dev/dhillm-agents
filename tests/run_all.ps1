$ErrorActionPreference = "Stop"
Write-Host "== Auto-fix common issues =="

# Remove illegal imports
Get-ChildItem -Recurse -Filter *.py | ForEach-Object {
  (Get-Content $_.FullName) -replace 'from importlib import bootstrap','' |
  Set-Content $_.FullName
}

# Ensure minimal healthz exists
if (!(Test-Path api/healthz.py)) {
@'
from fastapi import FastAPI
app = FastAPI()
@app.get("/api/healthz")
def healthz(): return {"ok": True}
'@ | Set-Content api/healthz.py }

# Normalize requirements.txt pins (dedupe keeps first)
$reqPath="requirements.txt"
$lines = Get-Content $reqPath | Where-Object { $_.Trim() -ne "" -and -not $_.Trim().StartsWith("#") }
$seen=@{}
$dedup=@()
foreach($l in $lines){ $n=$l.Split("==")[0].Trim().ToLower(); if(-not $seen.ContainsKey($n)){ $seen[$n]=$true; $dedup+= $l } }
$dedup | Set-Content $reqPath

Write-Host "== Install deps =="
python -m pip install -U pip
pip install -r requirements.txt fastapi[all] uvicorn pytest

Write-Host "== Run pytest =="
python -m pytest -q tests/import_sanity.py tests/pins_check.py tests/vercel_config_check.py tests/smoke_local.py