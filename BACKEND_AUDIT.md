# BACKEND AUDIT REPORT

## 1. API Design Issues

| Issue | File/Line | Problem | Impact |
|-------|-----------|---------|--------|
| **Inconsistent response envelopes** | analytics.py#L1-L50 vs copilot.py#L18-L27 | `/analytics/summary` returns raw dict, `/analytics/suppliers` returns raw array, but `/copilot/summary` returns wrapped object. No consistent structure. | Client must parse differently per endpoint. Breaking changes if structure changes. |
| **No pagination on list endpoints** | analytics.py#L42-L60 — `/analytics/suppliers` returns all rows without limit/offset. remaining.py — world events unsized. | If 10,000 suppliers exist, returns all in one response (~2MB). | OOM on mobile clients. Timeout on slow networks. |
| **Missing API versioning** | main.py#L220 | App version is "3.0.0" in FastAPI metadata, but no `/v1/`, `/v2/` route prefixes. All routers are unversioned. | No backward compatibility path. Breaking changes force all clients to upgrade simultaneously. |
| **Raw array responses (not enveloped)** | remaining.py#L38-L45, graph.py#L100-L105 | `/export/csv`, `/export/json` return streaming response directly without error envelope. `/graph/critical-paths` returns bare array. | Client can't distinguish between success and error without checking HTTP status. Non-uniform error handling. |
| **HTTP 503 for optional engines** | graph.py#L125-L128 — `raise HTTPException(status_code=503)` when TGNN unavailable. | 503 means "service temporarily unavailable" but TGNN is optional, not critical. | Frontend shows full error page instead of graceful degradation. |
| **No input validation on POST bodies** | copilot.py#L55-L70 — `body: dict` with no schema. remaining.py#L165 — dict body with no validation. | Accepts any JSON. No type checking, no required field validation. | Malformed requests crash or are silently ignored. |

---

## 2. Security Vulnerabilities

| Issue | File/Line | Severity | Problem |
|-------|-----------|----------|---------|
| **SHA-256 password hashing instead of bcrypt** | auth/utils.py#L17-L26 | 🔴 **CRITICAL** | `hash_password()` uses SHA-256 with 16-byte salt. No work factor. Susceptible to GPU/ASIC attacks. Produces 2^64 possible salts, not cryptographically random. | 
| **SQL injection in RLS string interpolation** | dependencies.py#L32-L33 | 🔴 **CRITICAL** | `db.execute(text(f"SET LOCAL app.current_tenant_id = '{tenant_id}'"))` — tenant_id is user-supplied, interpolated directly into SQL. Attacker can inject `'; DROP TABLE users; --` | 
| **Demo mode token bypass** | dependencies.py#L45-L52 | 🔴 **CRITICAL** | `if token == "demo" and _ALLOW_DEMO: return {...}` — ANY request with `Authorization: Bearer demo` bypasses all auth. No rate limiting. Attacker can access all endpoints as viewer. | 
| **CORS wildcard on methods** | main.py#L217 | 🟠 **HIGH** | `allow_methods=["*"]` allows DELETE, PATCH, OPTIONS from any origin. Should whitelist only GET, POST, OPTIONS. | 
| **JWT can be passed as query parameter** | auth_routes.py#L97 — `@router.get("/me", token: str = Query(...))` | 🟠 **HIGH** | Tokens in query strings are logged in access logs, browser history, referrer headers. Violates JWT best practices. Should use header-only. | 
| **Refresh tokens not rate-limited** | auth_routes.py#L56-L63 | 🟠 **HIGH** | `/auth/refresh` can be called unlimited times per second. Attacker can brute-force old refresh token hashes. No backoff, no account lockout. | 
| **No input validation on registration** | auth_routes.py#L12-L28 | 🟠 **HIGH** | Email/password accepted as raw Form strings with no length limits, no regex validation, no normalization. Attacker can register with 1MB email string. | 
| **Sensitive data in logs** | main.py#L165-L175 | 🟠 **HIGH** | Engine initialization errors logged with full exception stack traces. If stack trace contains SQL queries with secrets, leaked to logs. | 
| **No X-CSRF-Token on POST endpoints** | auth_routes.py#L31-L45 | 🟡 **MEDIUM** | `/auth/login`, `/auth/register` accept Form data over CORS without CSRF validation. Browser-based attacker can POST from any domain. | 

---

## 3. Database / ORM Issues

| Issue | File/Line | Problem |
|-------|-----------|---------|
| **N+1 query pattern in supplier analytics** | analytics.py#L42-L60 | Query aggregates suppliers (1 query) but then client loops over results and calls `get_analysis_result()` for EACH supplier separately in frontend. No eager loading. |
| **No indexes on critical columns** | database.py#L1-L30 — only creates tables, doesn't define indexes | SupplyData table queries on `supplier`, `sku`, `region`, `order_date`, `delivery_date` (WHERE, GROUP BY, ORDER BY) but no indexes defined. Full table scans on every analytic query. |
| **Refresh token cleanup never runs** | auth/service.py#L50-L80 | RefreshToken table grows unbounded. Expired tokens never deleted (no `DELETE FROM RefreshToken WHERE expires_at < NOW()`). GDPR violation. |
| **Missing transactions on upload pipeline** | upload.py#L200-L300 est. | Upload creates SupplyData rows in a loop without BEGIN TRANSACTION / ROLLBACK. If server crashes mid-upload, database is left with partial data, no way to retry atomically. |
| **Race condition in token refresh** | auth/service.py#L58-L72 | `generate_refresh_token()` creates new token but doesn't explicitly revoke the old one in same transaction. Two simultaneous refresh requests could both succeed with different tokens. |
| **Missing CASCADE DELETE on foreign keys** | models/*.py est. | If User is deleted, RefreshToken, AuditLog, UploadHistory orphaned. No referential integrity. |

---

## 4. Error Handling Gaps

| Issue | File/Line | Problem |
|-------|-----------|---------|
| **Inconsistent error response format** | analytics.py#L36-L40 vs remaining.py#L30 | Some endpoints return `{"error": "..."}`, others raise `HTTPException(status_code=404, detail="...")`. No unified error envelope. |
| **Generic 400/500 errors with no actionable detail** | auth_routes.py#L25-L28 | `HTTPException(status_code=400, detail=result["error"])` — passes raw string. Client gets "User with this email or username already exists" but doesn't know which field. |
| **No centralized exception handler** | main.py#L200-L250 | No `@app.exception_handler()` middleware. Unhandled exceptions in routers crash request with raw 500 + stack trace. Exposes internal structure. |
| **Silent failures on engine init** | main.py#L115-L150 | Engine failures logged but routers check `if engines.ai_copilot` and return generic 503. User doesn't know which engine failed or why. |
| **No request/response logging** | All routers | No middleware logs HTTP request/response for audit trail. Can't debug production issues or trace user actions. |

---

## 5. Code Quality

| Issue | File/Line | Problem |
|-------|-----------|---------|
| **Bloated upload.py with mixed concerns** | upload.py#L1-L200+ | Single file contains: column synonym tables (200 lines), parsing logic (300 lines), validation, file handling. Should be split into `schema.py`, `parser.py`, `validator.py`. |
| **Hardcoded demo data seeded in endpoint** | analytics.py#L103-L122 | World events seeded inline: `if not events: db.add_all([WorldEvent(...), WorldEvent(...)])`. Should be in database migration or fixture. Runs every request if no data. |
| **Circular import via engines singleton** | graph.py#L82 — `from app.main import engines` | Routers import from main to get engine singletons. Main imports routers. Python allows this but makes testing hard. Should use dependency injection. |
| **Type hints incomplete** | auth_routes.py#L31-L45 — response return type not specified | `def register_user(...) -> ???` — endpoint doesn't declare return type. FastAPI can't generate proper OpenAPI schema. |
| **Config loaded at module level** | config.py#L10-L25 | `settings = Settings()` is module-level singleton. Can't override for tests. Should use FastAPI dependency. |
| **No request/response validation schemas** | copilot.py#L54-L55 — `body: dict` | POST endpoints accept raw `dict` without Pydantic schema. Should use `class AskRequest(BaseModel): question: str`. |
| **Functions over 100 lines** | upload.py#L200+ — upload handler estimated 150+ lines | Does file parsing, validation, DB insert, cache save all in one function. Should split into smaller composable functions. |
| **Hardcoded constants scattered** | config.py#L20 — `_DEFAULT_SECRET = "nexus-dev-secret..."` | Should be in `.env.example` not source code. upload.py — multiple hardcoded thresholds (0.8, 50, 100) should be config. |

---

## 6. Top 5 Priority Fixes (Ranked by Impact)

### **#1. Replace SHA-256 with bcrypt password hashing** 🔴 **CRITICAL**

**File**: auth/utils.py#L17-L33

**Current code**:
```python
def hash_password(password: str) -> str:
    """Hash a password with salt using SHA-256 (production: use bcrypt)."""
    salt = secrets.token_hex(16)
    hashed = hashlib.sha256(f"{salt}{password}".encode()).hexdigest()
    return f"{salt}:{hashed}"
```

**Why**: SHA-256 is fast (a feature for hashing, a bug for passwords). No work factor. GPU can try 1 billion hashes/second. Bcrypt has configurable cost factor.

**What to change**:
```python
import bcrypt

def hash_password(password: str) -> str:
    """Hash with bcrypt (cost=12)."""
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt(rounds=12)).decode()

def verify_password(password: str, hashed: str) -> bool:
    """Verify bcrypt hash."""
    return bcrypt.checkpw(password.encode(), hashed.encode())
```

**Impact**: 🔥 **Eliminates GPU brute-force attacks. Production-grade security.**

---

### **#2. Fix SQL injection in RLS tenant isolation**

**File**: dependencies.py#L30-L35

**Current code**:
```python
db.execute(text(f"SET LOCAL app.current_tenant_id = '{tenant_id}'"))
```

**Why**: String interpolation. Attacker can pass `'; DROP TABLE users; --` as tenant_id.

**What to change**:
```python
from sqlalchemy import text, bindparam

db.execute(text("SET LOCAL app.current_tenant_id = :tenant_id"), {"tenant_id": tenant_id})
```

**Impact**: 🔥 **Closes SQL injection vector.**

---

### **#3. Add pagination to all list endpoints**

**File**: analytics.py#L42-L60, remaining.py#L85+

**Current code**:
```python
@router.get("/suppliers")
def supplier_analytics(...):
    rows = db.query(...).all()  # ← NO LIMIT
    return [...]
```

**Why**: Returns entire table. No limit/offset. Crashes on large datasets.

**What to change**:
```python
from pydantic import BaseModel

class PaginationParams(BaseModel):
    skip: int = 0
    limit: int = 50  # Default 50, max 100

@router.get("/suppliers")
def supplier_analytics(skip: int = 0, limit: int = 50, ...):
    limit = min(limit, 100)  # Cap at 100
    rows = db.query(...).offset(skip).limit(limit).all()
    total = db.query(func.count(...)).scalar()
    return {
        "data": [...],
        "total": total,
        "skip": skip,
        "limit": limit
    }
```

**Impact**: 🔥 **Prevents OOM. Enables scalable queries.**

---

### **#4. Remove demo mode token bypass + add rate limiting**

**File**: dependencies.py#L45-L52, auth_routes.py#L56-L63

**Current code**:
```python
if token == "demo" and _ALLOW_DEMO:
    return {"sub": "demo@nexus.ai", "role": "viewer", "uid": 0, "demo": True}
```

**Why**: Hardcoded magic token bypasses auth entirely. No rate limiting on `/auth/refresh`.

**What to change**:
```python
# Use fixed demo user ID, not magic token
async def require_auth(authorization: Optional[str] = Header(None)):
    if _ALLOW_DEMO and authorization is None:
        return {"sub": "demo@nexus.ai", "role": "viewer", "uid": 0, "demo": True}
    # ... normal JWT validation
```

**Add rate limiting middleware**:
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app = FastAPI(...)

@router.post("/auth/refresh")
@limiter.limit("5/minute")
def refresh_token(...):
    ...
```

**Impact**: 🔥 **Closes token bypass. Blocks brute force attacks.**

---

### **#5. Implement centralized error handling middleware + Pydantic schemas**

**File**: main.py#L200+, routers/auth_routes.py#L54-L55

**Current code**:
```python
# main.py - no global error handler
# auth_routes.py
def copilot_ask(body: dict, ...):
    question = body.get("question", "")  # ← No validation
```

**Why**: Inconsistent error responses. No input validation. Raw dict params.

**What to change**:
```python
# schemas.py
from pydantic import BaseModel, EmailStr

class RegisterRequest(BaseModel):
    email: EmailStr
    username: str
    password: str
    full_name: str = ""
    role: str = "analyst"

class AskRequest(BaseModel):
    question: str

# main.py
from fastapi.exceptions import RequestValidationError

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Unhandled error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "code": "INTERNAL_SERVER_ERROR",
            "message": "An internal error occurred.",
            "request_id": request.headers.get("X-Request-ID")
        }
    )

# auth_routes.py
@router.post("/register")
def register_user(req: RegisterRequest, ...):
    # Pydantic validates automatically
    result = AuthService.register(db, req.email, req.username, req.password, req.full_name, req.role)
```

**Impact**: 🔥 **Unified error handling. Automatic input validation. Better API schema generation.**

---

## Summary

**Verdict**: Backend is **functionally solid** (good architecture, engine pattern, lifespan management) but has **critical security gaps** and **API inconsistencies**.

**Severity**: 🔴 **HIGH** — Production-grade code with development-grade security.

- ✅ Good lifespan management, engine isolation, CORS config foundation
- ✅ Clean router separation, good use of dependencies
- ❌ **SHA-256 passwords** (not bcrypt)
- ❌ **SQL injection** in RLS
- ❌ **Auth bypass** (demo token)
- ❌ **No rate limiting**
- ❌ **No pagination**
- ❌ **Inconsistent errors**

**Time to fix**: ~3 days for a senior backend engineer (1 day security fixes, 1 day pagination + validation, 1 day error handling + refactoring).
