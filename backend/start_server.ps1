# Startup script for SynChain 2.0 Backend
Write-Host "Starting SynChain 2.0 Backend..." -ForegroundColor Yellow
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
Set-Location $scriptDir
$env:PYTHONPATH = "."
$venvPath = Join-Path $scriptDir "..\.venv\Scripts\uvicorn.exe"
& $venvPath main:app --host 0.0.0.0 --port 8000 --reload
