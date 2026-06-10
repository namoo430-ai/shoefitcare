# 로컬 데모 (--reload 필수: api.py HTML/세션은 import 시점에 로드됨)
Set-Location $PSScriptRoot\..
Write-Host "Starting demo at http://127.0.0.1:8001/demo (build check: /health/build)"
python -m uvicorn api:app --host 127.0.0.1 --port 8001 --reload
