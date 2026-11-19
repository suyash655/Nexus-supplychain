# Deployment Guide & Production Checklist

This guide covers deployment procedures, environment configuration, containerization, and secrets management for **NEXUS: Supply Chain Risk Intelligence Platform**.

---

## 1. Required Secrets & Environment Variables

When deploying to staging or production, ensure the following environment variables and GitHub Actions secrets are configured:

### 1.1 Core Backend Settings

| Variable | Required | Staging / Prod Value | Description |
|---|---|---|---|
| `SECRET_KEY` | **Yes** | 64+ char random hex | Secret key for signing JWT tokens and encryption. Generate with: `openssl rand -hex 32` |
| `ALLOW_DEMO` | **Yes** | `false` | Disables unauthenticated viewer access and forces valid JWTs on all API routes. |
| `DATABASE_URL` | **Yes** | `postgresql://user:pass@host:5432/nexus` | Production PostgreSQL connection string. (SQLite is used only for local dev). |
| `CORS_ORIGINS` | **Yes** | `https://nexus.yourcompany.com` | Comma-separated list of allowed frontend origins. Never use `*` in production. |
| `LLM_PROVIDER` | No | `groq`, `bedrock`, or `offline` | Provider for agent action drafting. Defaults to `offline` (safe deterministic fallback). |
| `GROQ_API_KEY` | Conditional | `gsk_...` | Required if `LLM_PROVIDER=groq`. |
| `AWS_ACCESS_KEY_ID` | Conditional | `AKIA...` | Required if `LLM_PROVIDER=bedrock`. |
| `AWS_SECRET_ACCESS_KEY` | Conditional | Secret | Required if `LLM_PROVIDER=bedrock`. |
| `AWS_REGION` | Conditional | `us-east-1` | AWS region where Bedrock model access is enabled. |
| `MAX_UPLOAD_BYTES` | No | `52428800` (50 MB) | Maximum permitted CSV/spreadsheet upload payload size. |
| `MAX_ANALYSIS_ROWS` | No | `100000` | Maximum rows parsed and analyzed per file to prevent memory exhaustion. |

### 1.2 Observability & Tracing (Optional)

| Variable | Staging / Prod Value | Description |
|---|---|---|
| `LANGFUSE_PUBLIC_KEY` | `pk-lf-...` | Langfuse public key for agent execution traces and token metrics. |
| `LANGFUSE_SECRET_KEY` | `sk-lf-...` | Langfuse secret key. |
| `LANGFUSE_HOST` | `https://cloud.langfuse.com` | Langfuse API host endpoint. |

### 1.3 Frontend Environment

| Variable | Staging / Prod Value | Description |
|---|---|---|
| `NEXT_PUBLIC_API_URL` | `https://api.nexus.yourcompany.com` | Base URL of the FastAPI backend reachable by the user's browser. |

---

## 2. Docker Deployment

NEXUS includes hardened multi-stage Dockerfiles for both services.

### 2.1 Running Locally with Docker Compose

```bash
# 1. Copy the template environment file
cp .env.example .env

# 2. Build and launch all services
docker compose up --build -d

# 3. Verify health
curl -f http://localhost:8000/health
curl -f http://localhost:3000/
```

### 2.2 Container Health Checks

- **Backend Container**:
  - Image: Python 3.12-slim
  - Healthcheck command: `python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"`
  - Interval: 30s, Timeout: 10s, Retries: 3
- **Frontend Container**:
  - Image: Node 20-alpine
  - Output: Standalone Next.js server (`node server.js`)
  - Healthcheck command: `node -e "fetch('http://localhost:3000').then(r => process.exit(r.ok ? 0 : 1)).catch(() => process.exit(1))"`

---

## 3. GitHub Actions CI/CD Pipeline

The repository includes two automated workflows:

1. **`CI` (`.github/workflows/ci.yml`)**:
   - Triggers on push and pull requests to `master` and `polish/**` branches.
   - Runs backend pytest test suite, Ruff linting, frontend lint/typecheck/build, Bandit SAST scanner, pip-audit, and agent injection smoke tests.
2. **`Deploy NEXUS` (`.github/workflows/deploy.yml`)**:
   - Manual workflow dispatch trigger (`workflow_dispatch`).
   - Requires setting GitHub repository secrets (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `DOCKER_REGISTRY_PAT`).

---

## 4. Production Hardening Checklist

Before exposing NEXUS to production traffic:

- [ ] **Rotate Secret Key**: Set a unique, 64-character `SECRET_KEY` in production secrets.
- [ ] **Enforce Authentication**: Set `ALLOW_DEMO=false` to reject unauthenticated requests.
- [ ] **Provision Managed PostgreSQL**: Migrate from local SQLite to RDS / Aurora PostgreSQL. Execute `backend/migrations/001_rls_tenant_isolation.sql` for tenant Row-Level Security.
- [ ] **Terminate TLS at Reverse Proxy**: Place Nginx, AWS Application Load Balancer, or Cloudflare in front of the application for HTTPS / TLS 1.3 termination.
- [ ] **Configure Redis for Rate Limiting**: In high-availability multi-instance setups, configure SlowAPI to use a Redis storage backend.
- [ ] **Configure CORS**: Explicitly list frontend domains in `CORS_ORIGINS`; ensure `*` is not permitted.
- [ ] **Set Resource Limits**: Configure container memory ceilings (e.g. 2 GB RAM limit per backend task) to prevent unbounded memory usage on massive CSV uploads.
