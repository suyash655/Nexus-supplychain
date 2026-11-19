"""
NEXUS — Input Sanitization and Prompt Boundary Guardrails
=========================================================
Protects the platform against:
1. Prompt injection via untrusted CSV fields (supplier names, notes, custom categories).
2. Spreadsheet formula injection (CSV/Excel DDE command execution).
3. Tool coercion via unauthorized tool invocations.
4. Delimiter collisions and control character exploits.
"""

import logging
import re
from typing import Any, List, Optional, Set

import pandas as pd  # type: ignore

logger = logging.getLogger("nexus.security.sanitize")

# Allowed agent tool calls — any tool call outside this set is blocked and logged
ALLOWED_AGENT_TOOLS: Set[str] = frozenset({
    "get_backup_suppliers",
    "simulate_reroute_cost",
    "retrieve_documents",
    "draft_action",
    "execute_action",
})

# Suspicious instruction patterns commonly found in prompt injections
_INJECTION_PATTERNS = [
    (re.compile(r"ignore\s+(all\s+)?(previous|prior|above)\s+instructions?", re.IGNORECASE), "instruction_override"),
    (re.compile(r"disregard\s+(all\s+)?(previous|prior)\s+instructions?", re.IGNORECASE), "instruction_override"),
    (re.compile(r"system\s*:\s*you\s+are", re.IGNORECASE), "role_impersonation"),
    (re.compile(r"you\s+are\s+now\s+(in\s+developer\s+mode|unrestricted)", re.IGNORECASE), "jailbreak_attempt"),
    (re.compile(r"(show|reveal|display|output|print|exfiltrate)\s+(system\s+prompt|instructions?|api_key|token)", re.IGNORECASE), "prompt_exfiltration"),
    (re.compile(r"tool_call\s*[:=\(]", re.IGNORECASE), "coerced_tool_call"),
    (re.compile(r"(drop|delete\s+from|insert\s+into|select\s+.*from)\s+[a-z0-9_]+", re.IGNORECASE), "sql_injection"),
    (re.compile(r"<\s*script[^>]*>", re.IGNORECASE), "html_xss"),
    (re.compile(r"javascript\s*:", re.IGNORECASE), "javascript_uri"),
    (re.compile(r"=cmd\|", re.IGNORECASE), "formula_dde_execution"),
]


def strip_control_characters(s: str) -> str:
    """Strip ASCII and Unicode control characters except standard whitespace (\\n, \\r, \\t)."""
    if not isinstance(s, str):
        return str(s) if s is not None else ""
    # Retain \t, \n, \r; strip other C0 and C1 control characters
    return re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F-\x9F]", "", s)


def normalize_whitespace(s: str) -> str:
    """Collapse runs of whitespace and trim ends."""
    if not isinstance(s, str):
        return ""
    return re.sub(r"[ \t]+", " ", s).strip()


def neutralize_delimiters(s: str) -> str:
    """
    Neutralize markdown code blocks, HTML/XML tags, and boundary marker collisions.
    Prevents untrusted text from breaking out of prompt framing tags.
    """
    if not isinstance(s, str):
        return ""
    # Disarm markdown backtick blocks
    s = s.replace("```", "'''")
    # Disarm angle bracket tags that could mimic boundary tags
    s = s.replace("<UNTRUSTED_DATA>", "[UNTRUSTED_DATA]")
    s = s.replace("</UNTRUSTED_DATA>", "[/UNTRUSTED_DATA]")
    s = s.replace("<data>", "[data]").replace("</data>", "[/data]")
    return s


def sanitize_text(val: Any, max_len: int = 500) -> str:
    """
    Full sanitization pipeline for free-text inputs:
    1. Null check and string coercion
    2. Control character removal
    3. Whitespace normalization
    4. Delimiter disarmament
    5. Length truncation
    """
    if val is None:
        return ""
    s = str(val)
    s = strip_control_characters(s)
    s = normalize_whitespace(s)
    s = neutralize_delimiters(s)
    if len(s) > max_len:
        s = s[:max_len]
    return s


def detect_suspicious_patterns(text: str) -> List[str]:
    """Scan text for known prompt injection and abuse signatures. Returns list of trigger names."""
    if not isinstance(text, str) or not text:
        return []
    triggers = []
    for pattern, name in _INJECTION_PATTERNS:
        if pattern.search(text):
            triggers.append(name)
            logger.warning("[SECURITY] Suspicious pattern '%s' detected in input: %s", name, text[:80])
    return triggers


def sanitize_csv_formula(val: Any) -> Any:
    """
    Neutralize CSV/Excel formula injection (OWASP CSV Injection).
    If a string starts with '=', '+', '-', '@', '\t', or '\r', prepend a single quote
    so spreadsheet software renders it as text rather than evaluating executable formulas.
    """
    if val is None or not isinstance(val, str):
        return val
    s = val.strip()
    if not s:
        return val
    if s[0] in ("=", "+", "-", "@", "\t", "\r"):
        return "'" + val
    return val


def sanitize_dataframe_formulas(df: pd.DataFrame) -> pd.DataFrame:
    """Return a copy of the DataFrame with all string cells neutralized against CSV formula injection."""
    df_clean = df.copy()
    for col in df_clean.columns:
        if df_clean[col].dtype == object or pd.api.types.is_string_dtype(df_clean[col]):
            df_clean[col] = df_clean[col].apply(lambda x: sanitize_csv_formula(x) if isinstance(x, str) else x)
    return df_clean


def format_untrusted_data_block(label: str, content: Any) -> str:
    """
    Wrap untrusted data in an explicitly delimited XML-style block.
    Instructs the LLM that content inside the block is strictly passive data.
    """
    sanitized_label = re.sub(r"[^a-zA-Z0-9_\-]", "", label)
    if isinstance(content, (dict, list)):
        import json
        sanitized_content = neutralize_delimiters(json.dumps(content, default=str))
    else:
        sanitized_content = sanitize_text(content, max_len=2000)

    # Detect any suspicious payloads for security auditing
    flags = detect_suspicious_patterns(str(content))
    if flags:
        logger.info("[AUDIT] Data block '%s' contains flagged signatures: %s", sanitized_label, flags)

    return (
        f"<UNTRUSTED_DATA label=\"{sanitized_label}\">\n"
        f"{sanitized_content}\n"
        f"</UNTRUSTED_DATA>"
    )


def is_tool_allowed(tool_name: str) -> bool:
    """Check if a tool name is on the authorized allowlist."""
    return tool_name in ALLOWED_AGENT_TOOLS


def validate_tool_call(tool_name: str, kwargs: Optional[dict] = None) -> bool:
    """
    Enforce tool authorization in code.
    Rejects disallowed tool names and logs any attempt to invoke unapproved capabilities.
    """
    if not is_tool_allowed(tool_name):
        logger.error("[SECURITY] Disallowed tool invocation attempt blocked: '%s'", tool_name)
        return False
    return True
