import hashlib
import json
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Iterable, Optional

import bcrypt

# JWT via PyJWT
try:
    import jwt as pyjwt  # type: ignore
except ImportError:
    pyjwt = None  # type: ignore

from app.core.config import settings  # Use centralized settings

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.JWT_ALGORITHM
TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES


# ── Password hashing ──

def hash_password(password: str) -> str:
    """Hash a password using bcrypt with a cost factor of 12.

    bcrypt generates and embeds a per-password salt automatically; the
    returned string is a single self-contained hash (≈60 chars) suitable
    for direct storage in the ``hashed_password`` column.
    """
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt(rounds=12)).decode()


def verify_password(password: str, hashed: str) -> bool:
    """Verify a plain-text password against a bcrypt hash.

    ``bcrypt.checkpw`` is timing-safe by design — no manual
    ``secrets.compare_digest`` wrapper is needed.
    """
    try:
        return bcrypt.checkpw(password.encode(), hashed.encode())
    except Exception:
        return False


# ── Access tokens ──

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a short-lived JWT access token (default: 60 min)."""
    if pyjwt is None:
        # Fallback: simple base64 token if PyJWT not installed
        import base64
        payload = json.dumps({**data, "exp": str(datetime.now(timezone.utc))})
        return base64.b64encode(payload.encode()).decode()

    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=TOKEN_EXPIRE_MINUTES)
    )
    to_encode["exp"] = expire
    to_encode["type"] = "access"
    return pyjwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> Optional[dict]:
    """Decode and validate a JWT access token. Returns None on any error."""
    if pyjwt is None:
        import base64
        try:
            return json.loads(base64.b64decode(token).decode())
        except Exception:
            return None
    try:
        payload = pyjwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        # Reject refresh tokens presented as access tokens
        if payload.get("type") == "refresh":
            return None
        return payload
    except Exception:
        return None


# ── Refresh tokens ──

def generate_refresh_token() -> tuple[str, str]:
    """
    Generate a cryptographically random refresh token.

    Returns:
        (raw_token, token_hash)  —  store only the hash in the DB,
        send the raw token to the client.
    """
    raw = secrets.token_urlsafe(48)
    token_hash = _hash_refresh_token(raw)
    return raw, token_hash


def _hash_refresh_token(raw: str) -> str:
    """SHA-256 hash of the raw refresh token for DB storage."""
    return hashlib.sha256(raw.encode()).hexdigest()


def verify_refresh_token_hash(raw: str, stored_hash: str) -> bool:
    """Constant-time comparison of a raw token against its stored hash."""
    expected = _hash_refresh_token(raw)
    return secrets.compare_digest(expected, stored_hash)


# ── API keys ──

def generate_api_key() -> tuple:
    """Generate an API key pair (raw key, hashed key)."""
    raw_key = f"nxs_{secrets.token_urlsafe(32)}"
    key_hash = hashlib.sha256(raw_key.encode()).hexdigest()
    return raw_key, key_hash


SENSITIVE_FIELD_HINTS = {"password", "passwd", "secret", "token", "api_key", "authorization", "ssn", "email", "phone"}


def mask_value(value: Any, visible: int = 4) -> Any:
    """Mask scalar values while preserving enough shape for audit/debug views."""
    if value is None:
        return None
    text = str(value)
    if len(text) <= visible:
        return "*" * len(text)
    return f"{text[:visible]}{'*' * max(4, len(text) - visible)}"


def mask_sensitive_data(payload: Any, extra_fields: Optional[Iterable[str]] = None) -> Any:
    """Recursively mask sensitive fields in dictionaries/lists."""
    sensitive = SENSITIVE_FIELD_HINTS | {field.lower() for field in (extra_fields or [])}
    if isinstance(payload, dict):
        masked: Dict[str, Any] = {}
        for key, value in payload.items():
            if any(hint in key.lower() for hint in sensitive):
                masked[key] = mask_value(value)
            else:
                masked[key] = mask_sensitive_data(value, sensitive)
        return masked
    if isinstance(payload, list):
        return [mask_sensitive_data(item, sensitive) for item in payload]
    return payload


def encrypt_field(value: str) -> str:
    """Lightweight reversible field protection for local/demo deployments."""
    import base64
    raw = value.encode()
    key = SECRET_KEY.encode() or b"nexus"
    protected = bytes(byte ^ key[index % len(key)] for index, byte in enumerate(raw))
    return base64.urlsafe_b64encode(protected).decode()


def decrypt_field(value: str) -> str:
    import base64
    raw = base64.urlsafe_b64decode(value.encode())
    key = SECRET_KEY.encode() or b"nexus"
    return bytes(byte ^ key[index % len(key)] for index, byte in enumerate(raw)).decode()
