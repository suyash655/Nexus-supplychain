/**
 * NEXUS — useEventStream Hook
 * ============================
 * EventSource-based hook for real-time SSE event streaming.
 * Connects to the backend SSE endpoint and dispatches events
 * to a local callback or state store.
 *
 * Usage:
 *   const { events, connected, error } = useEventStream({
 *     url: '/api/events/stream',
 *     tenantId: 'DEMO',
 *   });
 */

'use client'

import { useState, useEffect, useRef, useCallback } from 'react'

export interface SupplyChainEvent {
  id: number
  event_id: string
  event_type: string
  supplier_id: string
  severity: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL'
  description: string
  region?: string
  sku?: string
  impact_score?: number
  notes?: string
  tenant_id: string
  timestamp: string
}

interface UseEventStreamOptions {
  /** SSE endpoint URL */
  url?: string
  /** Tenant ID to filter events */
  tenantId?: string
  /** Maximum number of events to keep in state (oldest are dropped) */
  maxEvents?: number
  /** Auto-reconnect on disconnect */
  autoReconnect?: boolean
  /** Reconnect delay in ms */
  reconnectDelay?: number
  /** Called when a new event arrives */
  onEvent?: (event: SupplyChainEvent) => void
}

interface UseEventStreamReturn {
  /** Array of received events (newest first) */
  events: SupplyChainEvent[]
  /** Whether the SSE connection is active */
  connected: boolean
  /** Last error message, if any */
  error: string | null
  /** Number of events received since connection */
  eventCount: number
  /** Manually disconnect */
  disconnect: () => void
  /** Manually reconnect */
  reconnect: () => void
  /** Clear all stored events */
  clearEvents: () => void
}

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export function useEventStream(options: UseEventStreamOptions = {}): UseEventStreamReturn {
  const {
    url = '/api/events/stream',
    tenantId,
    maxEvents = 200,
    autoReconnect = true,
    reconnectDelay = 3000,
    onEvent,
  } = options

  const [events, setEvents] = useState<SupplyChainEvent[]>([])
  const [connected, setConnected] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [eventCount, setEventCount] = useState(0)

  const eventSourceRef = useRef<EventSource | null>(null)
  const reconnectTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null)
  const mountedRef = useRef(true)

  const buildUrl = useCallback(() => {
    const base = `${API_BASE}${url}`
    if (tenantId) {
      return `${base}?tenant_id=${encodeURIComponent(tenantId)}`
    }
    return base
  }, [url, tenantId])

  const disconnect = useCallback(() => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close()
      eventSourceRef.current = null
    }
    if (reconnectTimerRef.current) {
      clearTimeout(reconnectTimerRef.current)
      reconnectTimerRef.current = null
    }
    setConnected(false)
  }, [])

  const connect = useCallback(() => {
    // Close any existing connection
    if (eventSourceRef.current) {
      eventSourceRef.current.close()
    }

    const fullUrl = buildUrl()
    const es = new EventSource(fullUrl)
    eventSourceRef.current = es

    es.onopen = () => {
      if (mountedRef.current) {
        setConnected(true)
        setError(null)
      }
    }

    // Handle named 'new_event' events
    es.addEventListener('new_event', (e: MessageEvent) => {
      if (!mountedRef.current) return
      try {
        const eventData: SupplyChainEvent = JSON.parse(e.data)
        setEvents(prev => {
          const updated = [eventData, ...prev]
          return updated.slice(0, maxEvents)
        })
        setEventCount(prev => prev + 1)
        onEvent?.(eventData)
      } catch (err) {
        console.error('[useEventStream] Failed to parse event:', err)
      }
    })

    // Handle heartbeat
    es.addEventListener('heartbeat', () => {
      // Heartbeat received — connection is alive
    })

    // Handle default messages (connection ack, etc.)
    es.onmessage = (e: MessageEvent) => {
      // Generic message handler for non-named events
      try {
        const data = JSON.parse(e.data)
        if (data.type === 'connected') {
          console.log('[useEventStream] Connected to SSE stream')
        }
      } catch {
        // Ignore unparseable messages
      }
    }

    es.onerror = () => {
      if (!mountedRef.current) return
      setConnected(false)
      setError('SSE connection lost')
      es.close()
      eventSourceRef.current = null

      // Auto-reconnect
      if (autoReconnect) {
        reconnectTimerRef.current = setTimeout(() => {
          if (mountedRef.current) {
            console.log('[useEventStream] Reconnecting...')
            connect()
          }
        }, reconnectDelay)
      }
    }
  }, [buildUrl, maxEvents, autoReconnect, reconnectDelay, onEvent])

  const reconnect = useCallback(() => {
    disconnect()
    connect()
  }, [disconnect, connect])

  const clearEvents = useCallback(() => {
    setEvents([])
    setEventCount(0)
  }, [])

  useEffect(() => {
    mountedRef.current = true
    connect()

    return () => {
      mountedRef.current = false
      disconnect()
    }
  }, [connect, disconnect])

  return {
    events,
    connected,
    error,
    eventCount,
    disconnect,
    reconnect,
    clearEvents,
  }
}
