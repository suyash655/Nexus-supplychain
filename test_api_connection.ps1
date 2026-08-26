# Test Frontend-Backend Connection
$ErrorActionPreference = "Stop"

Write-Host "Testing Backend API..." -ForegroundColor Green

# Test 1: Health Check
Write-Host "1. Testing health endpoint..." -ForegroundColor Yellow
try {
    $health = [System.Net.WebRequest]::DefaultWebProxy = $null; (New-Object System.Net.WebClient).DownloadString("http://127.0.0.1:8000/system/health")
    Write-Host "   Health check passed" -ForegroundColor Green
    Write-Host "   Response: $health" -ForegroundColor Gray
} catch {
    Write-Host "   Health check failed: $_" -ForegroundColor Red
}

# Test 2: Analytics Summary
Write-Host "2. Testing analytics endpoint..." -ForegroundColor Yellow
try {
    $analytics = [System.Net.WebRequest]::DefaultWebProxy = $null; (New-Object System.Net.WebClient).DownloadString("http://127.0.0.1:8000/analytics/summary")
    Write-Host "   Analytics endpoint passed" -ForegroundColor Green
} catch {
    Write-Host "   Analytics endpoint failed: $_" -ForegroundColor Red
}

# Test 3: Graph Visualization
Write-Host "3. Testing graph endpoint..." -ForegroundColor Yellow
try {
    $graph = [System.Net.WebRequest]::DefaultWebProxy = $null; (New-Object System.Net.WebClient).DownloadString("http://127.0.0.1:8000/graph/visualization")
    Write-Host "   Graph endpoint passed" -ForegroundColor Green
} catch {
    Write-Host "   Graph endpoint failed: $_" -ForegroundColor Red
}

Write-Host "Backend API tests completed!" -ForegroundColor Green

Write-Host ""
Write-Host "Testing Frontend..." -ForegroundColor Green

# Test 4: Frontend accessibility
Write-Host "4. Testing frontend home page..." -ForegroundColor Yellow
try {
    $frontend = [System.Net.WebRequest]::DefaultWebProxy = $null; (New-Object System.Net.WebClient).DownloadString("http://127.0.0.1:3000")
    Write-Host "   Frontend home page passed" -ForegroundColor Green
} catch {
    Write-Host "   Frontend home page failed: $_" -ForegroundColor Red
}

Write-Host "Frontend tests completed!" -ForegroundColor Green
