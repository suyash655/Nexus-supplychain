/**
 * NEXUS — EventFeed Component
 * =============================
 * Real-time supply chain event feed powered by SSE.
 * Displays incoming events with severity indicators, timestamps,
 * and animated entry transitions.
 */

'use client'

import { useState } from 'react'
import { useEventStream, SupplyChainEvent } from '../hooks/useEventStream'
import { motion, AnimatePresence } from 'framer-motion'

const SEVERITY_CONFIG: Record<string, { color: string; bg: string; label: string }> = {
  CRITICAL: { color: '#ff4757', bg: 'rgba(255, 71, 87, 0.12)', label: 'CRIT' },
  HIGH:     { color: '#ff6b35', bg: 'rgba(255, 107, 53, 0.12)', label: 'HIGH' },
  MEDIUM:   { color: '#ffa502', bg: 'rgba(255, 165, 2, 0.12)',  label: 'MED' },
  LOW:      { color: '#7bed9f', bg: 'rgba(123, 237, 159, 0.12)', label: 'LOW' },
}

const EVENT_TYPE_ICONS: Record<string, string> = {
  DELAY: '⏱',
  DISRUPTION: '⚡',
  QUALITY_ISSUE: '🔍',
  SHORTAGE: '📦',
  GEOPOLITICAL: '🌍',
  NATURAL_DISASTER: '🌊',
}

interface EventFeedProps {
  tenantId?: string
  maxVisible?: number
  compact?: boolean
}

export function EventFeed({ tenantId = 'DEMO', maxVisible = 20, compact = false }: EventFeedProps) {
  const { events, connected, error, eventCount, clearEvents } = useEventStream({
    tenantId,
    maxEvents: 200,
  })
  const [expanded, setExpanded] = useState<string | null>(null)

  const visibleEvents = events.slice(0, maxVisible)

  const formatTime = (ts: string) => {
    const date = new Date(ts)
    const now = new Date()
    const diff = now.getTime() - date.getTime()
    if (diff < 60000) return 'Just now'
    if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`
    if (diff < 86400000) return `${Math.floor(diff / 3600000)}h ago`
    return date.toLocaleDateString()
  }

  return (
    <div style={{
      background: 'var(--background-surface, #0a0a0f)',
      border: '1px solid var(--background-border, rgba(255,255,255,0.06))',
      borderRadius: '12px',
      overflow: 'hidden',
    }}>
      {/* Header */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: compact ? '12px 16px' : '16px 20px',
        borderBottom: '1px solid var(--background-border, rgba(255,255,255,0.06))',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <div style={{
            width: '8px',
            height: '8px',
            borderRadius: '50%',
            background: connected ? '#7bed9f' : '#ff4757',
            boxShadow: connected ? '0 0 8px rgba(123,237,159,0.5)' : '0 0 8px rgba(255,71,87,0.5)',
            animation: connected ? 'pulse 2s infinite' : 'none',
          }} />
          <span style={{
            fontSize: '13px',
            fontWeight: 600,
            color: 'var(--text-primary, #e8e8ed)',
            letterSpacing: '0.02em',
          }}>
            Event Stream
          </span>
          <span style={{
            fontSize: '11px',
            color: 'var(--text-tertiary, #636366)',
            fontFamily: 'monospace',
          }}>
            {eventCount} events
          </span>
        </div>
        <div style={{ display: 'flex', gap: '8px' }}>
          {eventCount > 0 && (
            <button
              onClick={clearEvents}
              style={{
                fontSize: '11px',
                color: 'var(--text-tertiary, #636366)',
                background: 'none',
                border: 'none',
                cursor: 'pointer',
                padding: '2px 6px',
              }}
            >
              Clear
            </button>
          )}
          <span style={{
            fontSize: '10px',
            color: connected ? '#7bed9f' : '#ff4757',
            fontFamily: 'monospace',
          }}>
            {connected ? 'LIVE' : error || 'DISCONNECTED'}
          </span>
        </div>
      </div>

      {/* Event List */}
      <div style={{
        maxHeight: compact ? '300px' : '500px',
        overflowY: 'auto',
        padding: '4px 0',
      }}>
        {visibleEvents.length === 0 && (
          <div style={{
            padding: '40px 20px',
            textAlign: 'center',
            color: 'var(--text-disabled, #48484a)',
            fontSize: '13px',
          }}>
            <div style={{ fontSize: '24px', marginBottom: '8px' }}>📡</div>
            Waiting for events...
          </div>
        )}

        <AnimatePresence mode="popLayout">
          {visibleEvents.map((event) => {
            const severity = SEVERITY_CONFIG[event.severity] || SEVERITY_CONFIG.LOW
            const icon = EVENT_TYPE_ICONS[event.event_type] || '📋'
            const isExpanded = expanded === event.event_id

            return (
              <motion.div
                key={event.event_id}
                initial={{ opacity: 0, y: -20, height: 0 }}
                animate={{ opacity: 1, y: 0, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                transition={{ duration: 0.3, ease: 'easeOut' }}
                onClick={() => setExpanded(isExpanded ? null : event.event_id)}
                style={{
                  padding: compact ? '8px 16px' : '12px 20px',
                  borderBottom: '1px solid rgba(255,255,255,0.03)',
                  cursor: 'pointer',
                  transition: 'background 0.15s',
                }}
                whileHover={{ backgroundColor: 'rgba(255,255,255,0.02)' }}
              >
                <div style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '10px',
                }}>
                  {/* Severity badge */}
                  <span style={{
                    fontSize: '10px',
                    fontWeight: 700,
                    color: severity.color,
                    background: severity.bg,
                    padding: '2px 6px',
                    borderRadius: '4px',
                    fontFamily: 'monospace',
                    minWidth: '36px',
                    textAlign: 'center',
                  }}>
                    {severity.label}
                  </span>

                  {/* Icon */}
                  <span style={{ fontSize: '14px' }}>{icon}</span>

                  {/* Description */}
                  <span style={{
                    flex: 1,
                    fontSize: '12px',
                    color: 'var(--text-secondary, #aeaeb2)',
                    overflow: 'hidden',
                    textOverflow: 'ellipsis',
                    whiteSpace: isExpanded ? 'normal' : 'nowrap',
                  }}>
                    <strong style={{ color: 'var(--text-primary, #e8e8ed)' }}>
                      {event.supplier_id}
                    </strong>
                    {' — '}
                    {event.description}
                  </span>

                  {/* Timestamp */}
                  <span style={{
                    fontSize: '10px',
                    color: 'var(--text-disabled, #48484a)',
                    fontFamily: 'monospace',
                    whiteSpace: 'nowrap',
                  }}>
                    {formatTime(event.timestamp)}
                  </span>
                </div>

                {/* Expanded details */}
                <AnimatePresence>
                  {isExpanded && (
                    <motion.div
                      initial={{ opacity: 0, height: 0 }}
                      animate={{ opacity: 1, height: 'auto' }}
                      exit={{ opacity: 0, height: 0 }}
                      style={{
                        marginTop: '10px',
                        padding: '10px 12px',
                        background: 'rgba(255,255,255,0.02)',
                        borderRadius: '6px',
                        fontSize: '11px',
                        color: 'var(--text-tertiary, #636366)',
                        display: 'grid',
                        gridTemplateColumns: '1fr 1fr',
                        gap: '6px',
                      }}
                    >
                      <div><strong>Type:</strong> {event.event_type}</div>
                      <div><strong>Region:</strong> {event.region || '—'}</div>
                      <div><strong>SKU:</strong> {event.sku || '—'}</div>
                      <div><strong>Impact:</strong> {event.impact_score ?? '—'}</div>
                      {event.notes && (
                        <div style={{ gridColumn: '1 / -1' }}>
                          <strong>Notes:</strong> {event.notes}
                        </div>
                      )}
                    </motion.div>
                  )}
                </AnimatePresence>
              </motion.div>
            )
          })}
        </AnimatePresence>
      </div>

      {/* Pulse animation keyframes */}
      <style>{`
        @keyframes pulse {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.4; }
        }
      `}</style>
    </div>
  )
}
