import { useState, useEffect, useCallback, useRef } from "react";
import { apiFetch } from "@/lib/api";

export type ApiErrorCode = "network" | "timeout" | "client_4xx" | "server_5xx" | "parse";

export interface ApiError {
  code: ApiErrorCode;
  message: string;
  status?: number;
}

interface CacheEntry<T> {
  data: T;
  timestamp: number;
}

// Module-level singletons for cache and deduplication
const cache = new Map<string, CacheEntry<any>>();
const inflight = new Map<string, Promise<any>>();
const listeners = new Map<string, Set<() => void>>();
const reducedTtlEndpoints = new Set<string>(); // Endpoints that need reduced TTL

/**
 * Cache buster.
 * Call with an endpoint to invalidate just that endpoint.
 * Call with no args to flush the entire cache.
 */
export function invalidateApi(endpoint?: string) {
  if (endpoint) {
    cache.delete(endpoint);
    reducedTtlEndpoints.add(endpoint); // Mark for reduced TTL on next fetch
    listeners.get(endpoint)?.forEach((fn) => fn());
  } else {
    cache.clear();
    reducedTtlEndpoints.clear(); // Reset all TTL behaviors
    listeners.forEach((set) => set.forEach((fn) => fn()));
  }
}

/**
 * Mark endpoints for reduced TTL (5 seconds) to ensure fresh data after upload
 */
export function setReducedTtl(endpoint?: string) {
  if (endpoint) {
    reducedTtlEndpoints.add(endpoint);
  } else {
    reducedTtlEndpoints.add("/analytics/kpi");
    reducedTtlEndpoints.add("/analytics/trends");
    reducedTtlEndpoints.add("/analytics/suppliers");
    reducedTtlEndpoints.add("/analytics/regions");
    reducedTtlEndpoints.add("/analytics/delays");
    reducedTtlEndpoints.add("/system/health");
  }
}

/**
 * Reset reduced TTL behavior for specific endpoints.
 * Call this after data has stabilized to restore normal caching.
 */
export function resetReducedTtl(endpoint?: string) {
  if (endpoint) {
    reducedTtlEndpoints.delete(endpoint);
  } else {
    reducedTtlEndpoints.clear();
  }
}

/**
 * Force cache refresh - invalidates and immediately triggers refetch.
 * Call with an endpoint to force refresh just that endpoint.
 * Call with no args to force refresh the entire cache.
 */
export function forceRefreshApi(endpoint?: string) {
  // invalidateApi already notifies listeners, which triggers the refetch
  invalidateApi(endpoint);
}

interface UseApiOptions<T> {
  ttl?: number; // Time-to-live in milliseconds (default: 30000)
  fallback?: T; // Value to use when in demo mode and the request fails
  enabled?: boolean; // Skip fetching if false
  timeout?: number; // Request timeout in milliseconds (default: 8000)
  showError?: boolean; // Log a warning on failure (default: false)
  retryOnAuthError?: boolean; // Whether to retry on 401 errors (default: false)
}

function isDemoModeOn(): boolean {
  return typeof window !== "undefined" && localStorage.getItem("nexus_demo_mode") === "true";
}

function sameError(a: ApiError | null, b: ApiError): boolean {
  return !!a && a.code === b.code && a.message === b.message && a.status === b.status;
}

export function useApi<T>(path: string, options: UseApiOptions<T> = {}) {
  const {
    ttl = 30000,
    fallback,
    enabled = true,
    timeout = 8000,
    showError = false,
    retryOnAuthError = false,
  } = options;

  // Callers often pass an inline object as `fallback`. Its identity changes on
  // every render, so it must never be a dependency of fetchData. Read it from a ref.
  const fallbackRef = useRef<T | undefined>(fallback);
  fallbackRef.current = fallback;

  const [data, setData] = useState<T | null>(() => {
    // Synchronous cache hit on initial render
    if (enabled && cache.has(path)) {
      const entry = cache.get(path)!;
      const effectiveTtl = reducedTtlEndpoints.has(path) ? 5000 : ttl;
      if (Date.now() - entry.timestamp < effectiveTtl) {
        return entry.data as T;
      }
    }
    // Use fallback on initial render only if demo mode is enabled
    return isDemoModeOn() && fallback ? fallback : null;
  });

  const [loading, setLoading] = useState(!cache.has(path) && enabled);
  const [error, setError] = useState<ApiError | null>(null);
  const [isDemoMode, setIsDemoMode] = useState<boolean>(isDemoModeOn());

  const fetchRef = useRef(0);
  const authErrorCount = useRef(0);
  const retryTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

  const fetchData = useCallback(
    async (ignoreCache = false) => {
      if (!enabled) return;

      const demoMode = isDemoModeOn();
      setIsDemoMode(demoMode);

      // Cache check
      if (!ignoreCache && cache.has(path)) {
        const entry = cache.get(path)!;
        const effectiveTtl = reducedTtlEndpoints.has(path) ? 5000 : ttl;
        if (Date.now() - entry.timestamp < effectiveTtl) {
          setData(entry.data);
          setError(null);
          setLoading(false);
          return;
        }
      }

      // Only use fallback if explicitly in demo mode, so real data wins after upload
      const effectiveFallback = demoMode ? fallbackRef.current : undefined;

      const currentFetch = ++fetchRef.current;
      setLoading(true);
      setError(null);

      try {
        // Deduplication: if another component is fetching this, wait for it
        let reqPromise = inflight.get(path);
        if (!reqPromise) {
          const controller = new AbortController();
          const timeoutId = setTimeout(() => controller.abort(), timeout);

          reqPromise = apiFetch(path, { signal: controller.signal })
            .finally(() => {
              clearTimeout(timeoutId);
              inflight.delete(path);
            })
            .then(async (res) => {
              if (!res.ok) {
                const code: ApiErrorCode = res.status >= 500 ? "server_5xx" : "client_4xx";
                throw { code, message: res.statusText, status: res.status };
              }
              try {
                return await res.json();
              } catch {
                throw { code: "parse", message: "Failed to parse JSON response" };
              }
            })
            .catch((err) => {
              if (err?.name === "AbortError") {
                throw { code: "timeout", message: "Request timed out" };
              }
              if (err?.code) throw err; // Already formatted
              throw { code: "network", message: err?.message || "Network error" };
            });

          inflight.set(path, reqPromise);
        }

        const result = await reqPromise;

        // Only update state if this is still the most recent fetch call
        if (currentFetch === fetchRef.current) {
          authErrorCount.current = 0;
          cache.set(path, { data: result, timestamp: Date.now() });
          setData(result);
          setError(null);
          // Real data arrived, so leave demo mode
          if (isDemoModeOn()) {
            localStorage.removeItem("nexus_demo_mode");
          }
          setIsDemoMode(false);
        }
      } catch (err: any) {
        if (currentFetch === fetchRef.current) {
          const apiError = err as ApiError;

          // Handle 401 authentication errors
          if (apiError.status === 401) {
            authErrorCount.current += 1;

            if (!retryOnAuthError || authErrorCount.current >= 3) {
              setError((prev) => (sameError(prev, apiError) ? prev : apiError));
              setData(effectiveFallback ?? null);
            } else {
              // Retry on 401 if enabled, capped at 3 attempts
              if (retryTimer.current) clearTimeout(retryTimer.current);
              retryTimer.current = setTimeout(() => fetchData(true), 1000);
            }
            return;
          }

          // Identical errors keep the same object, so state does not change and nothing re-renders
          setError((prev) => (sameError(prev, apiError) ? prev : apiError));
          setData(effectiveFallback ?? null);

          // Keep this hook UI-agnostic; callers read `error` for UI feedback
          if (showError && typeof window !== "undefined") {
            console.warn("API Error:", apiError.message);
          }
        }
      } finally {
        if (currentFetch === fetchRef.current) {
          setLoading(false);
        }
      }
    },
    // `fallback` is intentionally absent: it is read through fallbackRef
    [path, ttl, enabled, timeout, showError, retryOnAuthError]
  );

  useEffect(() => {
    // New path or options: start with a clean auth-error counter
    authErrorCount.current = 0;

    fetchData();

    // Listener for manual invalidation
    const listener = () => fetchData(true);

    let set = listeners.get(path);
    if (!set) {
      set = new Set();
      listeners.set(path, set);
    }
    set.add(listener);

    return () => {
      set?.delete(listener);
      if (set?.size === 0) listeners.delete(path);
      if (retryTimer.current) {
        clearTimeout(retryTimer.current);
        retryTimer.current = null;
      }
    };
  }, [fetchData, path]);

  const retry = useCallback(() => fetchData(true), [fetchData]);

  return { data, loading, error, retry, isDemoMode };
}