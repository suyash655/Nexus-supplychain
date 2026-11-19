# Baseline Audit

Recorded on: 2026-11-15 (Windows host, Python 3.13.9, Node v24.8.0, npm 11.6.2).

## 1. Test Suite Results
- **Backend Tests (pytest):**
  - Command: `.\.venv\Scripts\pytest.exe backend/tests/`
  - Result: **17 passed, 0 failed**, 1 cache warning (`PytestCacheWarning: [Errno 13] Permission denied: 'D:\supex1\.pytest_cache\v\cache\nodeids'`) in 6.56s.
  - Test files:
    - `backend/tests/test_audit_fixes.py` (6 passed)
    - `backend/tests/test_health.py` (2 passed)
    - `backend/tests/test_phase4_backend.py` (9 passed)
- **Frontend Unit Tests (vitest):**
  - Command: `cd frontend && npm test`
  - Result: **1 passed, 0 failed** (`app/page.test.tsx`) in 2.04s.
- **Frontend Type Check:**
  - Command: `cd frontend && npx tsc --noEmit`
  - Result: **Passed (0 errors)**.

## 2. Startup Verification
- **Backend Startup:**
  - Tested importing `app.main` and executing `GET /health` via FastAPI TestClient:
  - Status: **200 OK**
  - Payload: `{"status": "ok", "db": "connected", "db_latency_ms": 3.53, "version": "0.1.0"}`
- **Production Secret Crash Guard:**
  - `backend/app/main.py:52` calls `settings.validate_production_secret()`. When `DEBUG=False` and `SECRET_KEY == "nexus-dev-secret-change-in-production"`, it raises `RuntimeError` and aborts startup as expected.

## 3. Docker & Container Builds
- **Local Docker Engine:**
  - `docker` is not installed on this local Windows host (`docker: The term 'docker' is not recognized`).
  - Docker build capability cannot be verified locally without Docker engine; relies on GitHub Actions or containerized CI.
- **Dockerfiles Present:**
  - `backend/Dockerfile`: Multi-stage build (`python:3.12-slim AS builder`, `python:3.12-slim AS runtime`), non-root user `nexus`, healthcheck via `curl http://localhost:8000/health`.
  - `frontend/Dockerfile.frontend`: Multi-stage build (`node:20-alpine AS builder`, `node:20-alpine AS runtime`), non-root user `nextjs`, healthcheck via `node -e "require('http').get(...)"`.
  - Root `docker-compose.yml` configures `backend` and `frontend` services with port mappings `8000:8000` and `3000:3000`.

## 4. Lint and Static Analysis
- **Python / Backend Linting:**
  - `ruff` not yet installed in `.venv`. Lint status unmeasured at baseline.
- **Frontend Linting (ESLint):**
  - Command: `cd frontend && npm run lint`
  - Result: **2 errors, 45 warnings**.
  - Errors:
    - `frontend/app/causal/page.tsx:183:86`: unescaped quote `"` in JSX.
    - `frontend/app/causal/page.tsx:183:103`: unescaped quote `"` in JSX.
  - Warnings: 45 warnings (predominantly `@typescript-eslint/no-unused-vars` and missing hook dependencies in `useCallback` / `useMemo`).

## 5. Coverage
- `pytest-cov` is not installed in `.venv`. Coverage unmeasured at baseline.

## 6. Repository Size and File Footprint
- **Total Workspace Size on Disk:** 2,224,505,255 bytes (~2.22 GB), including `.venv` (virtualenv), `frontend/node_modules/`, `infra/node_modules/`, and `.next/` build caches.
- **Tracked Git Repository Size:** 256 files, 7,352,055 bytes (~7.35 MB).
- **Tracked Files over 5 MB:** **0 files**.
- **Untracked Local Files over 5 MB:**
  - `data/synchain.db` (5,278,816 bytes)
  - `data/synchain.db-wal` (19,689,512 bytes)
  - Various binary artifacts inside `.venv/Lib/site-packages/` (OpenBLAS, PyDantic, Cryptography pyds) and `node_modules/` (SWC, Sharp).

## 7. Tracked Secrets & Databases
- Tracked database files (`*.db`): **None**.
- Tracked `.env` files: **None**.
- Local `.env` file exists at repository root and in `frontend/.env.local`, both properly excluded by `.gitignore`.
- `.vscode/settings.json` is currently tracked in git (targeted for untracking in Phase 1).

## 8. TODO / FIXME Audit
- Tracked files containing `TODO`: **7 occurrences**
  - `README.md`: 5 occurrences (placeholder comments and video URLs)
  - `docs/analysis/ingestion_and_ml_critique.md`: 1 occurrence
  - `docs/analysis/production_review.md`: 1 occurrence
- Tracked files containing `FIXME`: **0 occurrences**.
