# Start both backend and frontend servers
Write-Host "Starting NEXUS application..." -ForegroundColor Green

# Kill any existing processes on ports 8000 and 3000
Write-Host "Cleaning up existing processes..." -ForegroundColor Yellow
Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue | ForEach-Object { 
    try { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue } catch {}
}
Get-NetTCPConnection -LocalPort 3000 -ErrorAction SilentlyContinue | ForEach-Object { 
    try { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue } catch {}
}

# Start backend
Write-Host "Starting backend server on port 8000..." -ForegroundColor Yellow
$backend = Start-Process -FilePath "python" -ArgumentList "-m uvicorn app.main:app --host 127.0.0.1 --port 8000" -WorkingDirectory "backend" -PassThru -WindowStyle Hidden

# Wait for backend to start
Start-Sleep -Seconds 5

# Start frontend
Write-Host "Starting frontend server on port 3000..." -ForegroundColor Yellow
$frontend = Start-Process -FilePath "npm" -ArgumentList "run dev" -WorkingDirectory "frontend" -PassThru -WindowStyle Hidden

# Wait for frontend to start
Start-Sleep -Seconds 5

Write-Host ""
Write-Host "Servers started successfully!" -ForegroundColor Green
Write-Host "Backend: http://127.0.0.1:8000" -ForegroundColor Cyan
Write-Host "Frontend: http://localhost:3000" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C to stop both servers" -ForegroundColor Yellow

# Keep script running
try {
    while ($true) {
        Start-Sleep -Seconds 1
        # Check if processes are still running
        $backendRunning = Get-Process -Id $backend.Id -ErrorAction SilentlyContinue
        $frontendRunning = Get-Process -Id $frontend.Id -ErrorAction SilentlyContinue
        
        if (-not $backendRunning -or -not $frontendRunning) {
            Write-Host "One or more servers stopped unexpectedly" -ForegroundColor Red
            break
        }
    }
} finally {
    # Cleanup
    Write-Host "Stopping servers..." -ForegroundColor Yellow
    Stop-Process -Id $backend.Id -Force -ErrorAction SilentlyContinue
    Stop-Process -Id $frontend.Id -Force -ErrorAction SilentlyContinue
    Write-Host "Servers stopped" -ForegroundColor Green
}
