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

/**
 * Cache buster.
 * Call with an endpoint to invalidate just that endpoint.
 * Call with no args to flush the entire cache.
 */
export function invalidateApi(endpoint?: string) {
  if (endpoint) {
    cache.delete(endpoint);
    listeners.get(endpoint)?.forEach((fn) => fn());
  } else {
    cache.clear();
    listeners.forEach((set) => set.forEach((fn) => fn()));
  }
}

interface UseApiOptions<T> {
  ttl?: number; // Time-to-live in milliseconds (default: 30000)
  fallback?: T; // Value to use when data is null/error
  enabled?: boolean; // Skip fetching if false
  timeout?: number; // Request timeout in milliseconds (default: 8000)
}

export function useApi<T>(path: string, options: UseApiOptions<T> = {}) {
  const {
    ttl = 30000,
    fallback,
    enabled = true,
    timeout = 8000,
  } = options;

  const [data, setData] = useState<T | null>(() => {
    // Synchronous cache hit on initial render
    if (enabled && cache.has(path)) {
      const entry = cache.get(path)!;
      if (Date.now() - entry.timestamp < ttl) {
        return entry.data as T;
      }
    }
    return fallback ?? null;
  });

  const [loading, setLoading] = useState(!cache.has(path) && enabled);
  const [error, setError] = useState<ApiError | null>(null);

  const fetchRef = useRef(0);

  const fetchData = useCallback(async (ignoreCache = false) => {
    if (!enabled) return;

    // Check cache
    if (!ignoreCache && cache.has(path)) {
      const entry = cache.get(path)!;
      if (Date.now() - entry.timestamp < ttl) {
        setData(entry.data);
        setError(null);
        setLoading(false);
        return;
      }
    }

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
        cache.set(path, { data: result, timestamp: Date.now() });
        setData(result);
        setError(null);
      }
    } catch (err: any) {
      if (currentFetch === fetchRef.current) {
        setError(err as ApiError);
        setData(fallback ?? null);
      }
    } finally {
      if (currentFetch === fetchRef.current) {
        setLoading(false);
      }
    }
  }, [path, ttl, fallback, enabled, timeout]);

  useEffect(() => {
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
  }, [fetchData, path]);

  const retry = useCallback(() => fetchData(true), [fetchData]);

  return { data, loading, error, retry };
}
