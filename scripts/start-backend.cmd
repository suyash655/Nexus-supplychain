@echo off
setlocal

echo ============================================
echo   NEXUS Backend Server
echo   http://localhost:8000
echo   Keep this window OPEN!
echo ============================================

set "PROJECT_ROOT=%~dp0..\"
set "PYTHONPATH=%PROJECT_ROOT%backend"
set "DEBUG=true"

cd /d "%PROJECT_ROOT%backend"
if exist "%PROJECT_ROOT%.venv\Scripts\python.exe" (
    "%PROJECT_ROOT%.venv\Scripts\python.exe" -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
) else (
    python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
)
