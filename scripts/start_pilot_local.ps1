# 로컬 파일럿 서버 (8001). 기존 프로세스 정리 후 uvicorn 시작.
$ErrorActionPreference = "SilentlyContinue"
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

Get-CimInstance Win32_Process -Filter "Name='python.exe'" |
  Where-Object { $_.CommandLine -match 'api:app|uvicorn' } |
  ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }

Get-NetTCPConnection -LocalPort 8001 -State Listen -ErrorAction SilentlyContinue |
  ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }

Start-Sleep -Seconds 2

Write-Host ""
Write-Host "=== ShoefitCare pilot (local) ===" -ForegroundColor Cyan
Write-Host "Starting: python -m uvicorn api:app --reload --host 127.0.0.1 --port 8001"
Write-Host ""
Write-Host "  Pilot (naver_sms): http://127.0.0.1:8001/pilot?product_id=SR266&src=naver_sms"
Write-Host "  Short link:        http://127.0.0.1:8001/n/1"
Write-Host "  Health/build:      http://127.0.0.1:8001/health/build"
Write-Host ""
Write-Host "  Preflight (other terminal): python scripts/preflight_naver_test_day.py"
Write-Host "  Doc: docs/runbooks/naver/PILOT_LOCAL_START.md"
Write-Host ""

python -m uvicorn api:app --reload --host 127.0.0.1 --port 8001
