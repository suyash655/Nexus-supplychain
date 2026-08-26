# NEXUS Backend Starter
# Right-click this file → "Run with PowerShell"
# Keep this window OPEN while using the app!

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  NEXUS Backend Server" -ForegroundColor Cyan
Write-Host "  http://localhost:8000" -ForegroundColor Yellow
Write-Host "  Keep this window OPEN!" -ForegroundColor Red
Write-Host "============================================" -ForegroundColor Cyan

$env:PYTHONPATH = "$PSScriptRoot\backend"
$env:DEBUG = "true"
Set-Location "$PSScriptRoot\backend"

& "$PSScriptRoot\.venv\Scripts\python.exe" -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
