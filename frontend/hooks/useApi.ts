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
const reducedTtlEndpoints = new Set<string>(); // Track endpoints that need reduced TTL

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
    // Mark all common analytics endpoints for reduced TTL
    reducedTtlEndpoints.add("/analytics/kpi");
    reducedTtlEndpoints.add("/analytics/trends");
    reducedTtlEndpoints.add("/analytics/suppliers");
    reducedTtlEndpoints.add("/analytics/regions");
    reducedTtlEndpoints.add("/analytics/delays");
    reducedTtlEndpoints.add("/system/health");
  }
}

/**
 * Reset reduced TTL behavior for specific endpoints
 * Call this after data has stabilized to restore normal caching
 */
export function resetReducedTtl(endpoint?: string) {
  if (endpoint) {
    reducedTtlEndpoints.delete(endpoint);
  } else {
    reducedTtlEndpoints.clear();
  }
}

/**
 * Force cache refresh - invalidates and immediately triggers refetch
 * Call with an endpoint to force refresh just that endpoint.
 * Call with no args to force refresh entire cache.
 */
export function forceRefreshApi(endpoint?: string) {
  invalidateApi(endpoint);
  // Force immediate refetch by calling all listeners
  if (endpoint) {
    listeners.get(endpoint)?.forEach((fn) => fn());
  } else {
    listeners.forEach((set) => set.forEach((fn) => fn()));
  }
}

interface UseApiOptions<T> {
  ttl?: number; // Time-to-live in milliseconds (default: 30000)
  fallback?: T; // Value to use when data is null/error
  enabled?: boolean; // Skip fetching if false
  timeout?: number; // Request timeout in milliseconds (default: 8000)
  showError?: boolean; // Show error toast on failure (default: false)
  retryOnAuthError?: boolean; // Whether to retry on 401 errors (default: false)
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

  const [data, setData] = useState<T | null>(() => {
    // Synchronous cache hit on initial render
    if (enabled && cache.has(path)) {
      const entry = cache.get(path)!;
      // Use reduced TTL (5 seconds) for endpoints that were recently invalidated
      const effectiveTtl = reducedTtlEndpoints.has(path) ? 5000 : ttl;
      if (Date.now() - entry.timestamp < effectiveTtl) {
        return entry.data as T;
      }
    }
    // Use fallback on initial render if demo mode is enabled
    const demoMode = typeof window !== "undefined" ? localStorage.getItem("nexus_demo_mode") === "true" : false;
    return demoMode && fallback ? fallback : null;
  });

  const [loading, setLoading] = useState(!cache.has(path) && enabled);
  const [error, setError] = useState<ApiError | null>(null);
  const [isDemoMode, setIsDemoMode] = useState(typeof window !== "undefined" ? localStorage.getItem("nexus_demo_mode") === "true" : false);

  const fetchRef = useRef(0);
  const authErrorCount = useRef(0);

  const fetchData = useCallback(async (ignoreCache = false) => {
    if (!enabled) return;

    // Check for demo mode inline to avoid dependency issues
    const demoMode = typeof window !== "undefined" ? localStorage.getItem("nexus_demo_mode") === "true" : false;
    setIsDemoMode(demoMode);

    // Check cache
    if (!ignoreCache && cache.has(path)) {
      const entry = cache.get(path)!;
      // Use reduced TTL (5 seconds) for endpoints that were recently invalidated
      const effectiveTtl = reducedTtlEndpoints.has(path) ? 5000 : ttl;
      if (Date.now() - entry.timestamp < effectiveTtl) {
        setData(entry.data);
        setError(null);
        setLoading(false);
        return;
      }
    }

    // Only use fallback if explicitly in demo mode
    // This ensures real data is shown when available after upload
    const effectiveFallback = demoMode ? fallback : undefined;

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
            inflight.delete(path); // Cleanup
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
            if (err.name === "AbortError") {
              throw { code: "timeout", message: "Request timed out" };
            }
            if (err.code) throw err; // Already formatted
            throw { code: "network", message: err.message || "Network error" };
          });

        inflight.set(path, reqPromise);
      }

      const result = await reqPromise;

      // Only update state if this is still the most recent fetch call
      if (currentFetch === fetchRef.current) {
        authErrorCount.current = 0; // Reset auth error count on success
        cache.set(path, { data: result, timestamp: Date.now() });
        setData(result);
        setError(null);
        // If we got real data, exit demo mode
        if (typeof window !== "undefined" && localStorage.getItem("nexus_demo_mode") === "true") {
          localStorage.removeItem("nexus_demo_mode");
        }
        setIsDemoMode(false);
      }
    } catch (err: any) {
      if (currentFetch === fetchRef.current) {
        const error = err as ApiError;

        // Handle 401 authentication errors
        if (error.status === 401) {
          authErrorCount.current += 1;

          // Don't retry on 401 errors unless explicitly requested and limit retries
          if (!retryOnAuthError || authErrorCount.current >= 3) {
            setError(error);
            setLoading(false); // Stop loading state
            if (effectiveFallback) {
              setData(effectiveFallback);
            } else {
              setData(null);
            }
          } else {
            // Retry once on 401 if retryOnAuthError is enabled
            setTimeout(() => fetchData(true), 1000);
          }
          return; // Exit early for 401 errors
        }

        setError(error);
        // Only use fallback if in demo mode
        if (effectiveFallback) {
          setData(effectiveFallback);
        } else {
          setData(null);
        }

        // Keep this hook UI-agnostic; callers that need toast feedback should
        // read `error` and render or notify from component scope.
        if (showError && typeof window !== "undefined") {
          console.warn("API Error:", err.message);
        }
      }
    } finally {
      if (currentFetch === fetchRef.current) {
        setLoading(false);
      }
    }
  }, [path, ttl, fallback, enabled, timeout, showError, retryOnAuthError]);

  useEffect(() => {
    // Don't fetch if we already have a 401 error to prevent retry loops
    if (error?.status === 401 && authErrorCount.current >= 1) {
      return;
    }

    fetchData();

    // Setup listener for manual invalidation
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
    };
  }, [fetchData, path, error?.status]);

  const retry = useCallback(() => fetchData(true), [fetchData]);

  return { data, loading, error, retry, isDemoMode };
}
