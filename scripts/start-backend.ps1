# NEXUS Backend Starter
# Right-click this file → "Run with PowerShell"
# Keep this window OPEN while using the app!

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  NEXUS Backend Server" -ForegroundColor Cyan
Write-Host "  http://localhost:8000" -ForegroundColor Yellow
Write-Host "  Keep this window OPEN!" -ForegroundColor Red
Write-Host "============================================" -ForegroundColor Cyan

$repoRoot = Split-Path -Parent $PSScriptRoot
$env:PYTHONPATH = "$repoRoot\backend"
$env:DEBUG = "true"
Set-Location "$repoRoot\backend"

$venvPython = "$repoRoot\.venv\Scripts\python.exe"
if (Test-Path $venvPython) {
    & $venvPython -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
} else {
    python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
}
