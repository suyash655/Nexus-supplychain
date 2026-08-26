# NEXUS Startup Guide

## Quick Start

### Option 1: Start Both Servers Automatically
```powershell
.\start-all.ps1
```

This script will:
- Kill any existing processes on ports 8000 and 3000
- Start the backend server on http://127.0.0.1:8000
- Start the frontend server on http://localhost:3000
- Monitor both servers and stop them when you press Ctrl+C

### Option 2: Start Servers Manually

**Terminal 1 - Backend:**
```powershell
cd backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

**Terminal 2 - Frontend:**
```powershell
cd frontend
npm run dev
```

## Testing the Connection

Run the API connection test:
```powershell
.\test_api_connection.ps1
```

This will test:
- Backend health endpoint
- Analytics endpoint
- Graph visualization endpoint
- Frontend accessibility

## Verification

Once both servers are running:
1. Open http://localhost:3000 in your browser
2. Navigate to different pages (Dashboard, Graph, Analytics, etc.)
3. Verify that data loads correctly from the backend

## Troubleshooting

### Port Already in Use
If you see "port already in use" errors:
```powershell
# Kill process on port 8000
netstat -ano | findstr :8000
taskkill /F /PID <PID>

# Kill process on port 3000
netstat -ano | findstr :3000
taskkill /F /PID <PID>
```

### CORS Errors
The backend is configured to allow requests from:
- http://localhost:3000
- http://127.0.0.1:3000
- http://localhost:8000
- http://127.0.0.1:8000
- http://172.20.138.103:3000

If you need to add more origins, edit `backend/app/core/config.py`.

### Frontend Not Connecting
Ensure the frontend is configured with the correct API URL in `frontend/.env.local`:
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Running Tests

**Backend Tests:**
```powershell
cd backend
python -m pytest tests/ -v
```

**Frontend Unit Tests:**
```powershell
cd frontend
npm test
```

**E2E Tests:**
```powershell
cd frontend
$env:NEXT_PUBLIC_API_URL='http://127.0.0.1:8000'
$env:PLAYWRIGHT_BASE_URL='http://127.0.0.1:3000'
npx playwright test --config=playwright.config.mjs
```

## Stopping Servers

If using the automated script, press Ctrl+C to stop both servers.

If running manually, press Ctrl+C in each terminal window.

## Configuration Files

- **Backend Config:** `backend/app/core/config.py`
- **Frontend Env:** `frontend/.env.local`
- **CORS Settings:** `backend/app/main.py` (middleware section)
