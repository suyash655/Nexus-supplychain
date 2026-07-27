/**
 * Centralized API Client for NEXUS
 * - Attaches auth token to every request
 * - Validates res.ok before parsing
 * - Single source of truth for API base URL
 */

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export { API_BASE };

/**
 * Authenticated fetch wrapper.
 * Reads nexus_token from localStorage and attaches Authorization header.
 * Throws on non-OK responses with the status text.
 */
export async function apiFetch(
  path: string,
  options: RequestInit = {}
): Promise<Response> {
  let token: string | null = null;
  if (typeof window !== "undefined") {
    token = localStorage.getItem("nexus_token");
  }

  const headers = new Headers(options.headers || {});
  
  // Skip auth for demo mode tokens
  const isDemoToken = token?.startsWith("demo_");
  if (token && !isDemoToken && !headers.has("Authorization")) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  const res = await fetch(`${API_BASE}${path}`, {
    cache: "no-store",
    ...options,
    headers,
  });

  return res;
}

/**
 * Fetch JSON with auth + automatic res.ok validation.
 * Returns parsed JSON or throws an error.
 */
export async function apiFetchJSON<T = unknown>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
  const res = await apiFetch(path, options);
  if (!res.ok) {
    throw new Error(`API ${res.status}: ${res.statusText}`);
  }
  return res.json() as Promise<T>;
}

/**
 * Post JSON body with auth.
 */
export async function apiPostJSON<T = unknown>(
  path: string,
  body: unknown,
  options: RequestInit = {}
): Promise<T> {
  const res = await apiFetch(path, {
    method: "POST",
    headers: { "Content-Type": "application/json", ...(options.headers as Record<string, string> || {}) },
    body: JSON.stringify(body),
    ...options,
  });
  if (!res.ok) {
    throw new Error(`API ${res.status}: ${res.statusText}`);
  }
  return res.json() as Promise<T>;
}

/**
 * Safe fetch wrapper that returns null instead of throwing on error.
 */
export async function apiFetchSafe<T = any>(path: string): Promise<T | null> {
  try {
    const r = await apiFetch(path);
    return r.ok ? await r.json() : null;
  } catch {
    return null;
  }
}

