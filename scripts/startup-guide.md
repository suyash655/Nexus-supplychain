# NEXUS Startup Guide

## Quick Start

### Option 1: Start Both Servers Automatically (Windows PowerShell)
```powershell
.\scripts\start-all.ps1
```

This script will:
- Terminate lingering processes on ports 8000 and 3000
- Start the backend server on `http://127.0.0.1:8000`
- Start the frontend server on `http://localhost:3000`
- Monitor both servers and stop them when you press Ctrl+C

### Option 2: Start Servers Manually

**Terminal 1 - Backend:**
```powershell
cd backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

**Terminal 2 - Frontend:**
```powershell
cd frontend
npm run dev
```

## Testing the Connection

Run the API connection test script:
```powershell
.\scripts\test_api_connection.ps1
```

This will test:
- Backend health endpoint (`/health`)
- Analytics endpoint (`/analytics/summary`)
- Graph visualization endpoint (`/graph/visualization`)
- Frontend accessibility (`http://127.0.0.1:3000`)

## Verification

Once both servers are running:
1. Open `http://localhost:3000` in your browser
2. Navigate to Dashboard, Graph, Analytics, and Mitigation pages
3. Verify that data loads from the backend
