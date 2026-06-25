'use client'
import { useState, useRef, useEffect } from 'react'
import './NexusChat.css'

interface Message { role: 'user' | 'assistant'; content: string; sources?: string[] }

export function NexusChat() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const bottomRef = useRef<HTMLDivElement>(null)

  const send = async () => {
    if (!input.trim()) return
    const userMsg: Message = { role: 'user', content: input }
    setMessages(prev => [...prev, userMsg])
    setInput('')
    setLoading(true)

    try {
      // In production, get the real tenant ID from the auth context
      const res = await fetch('http://localhost:8000/api/rag/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: input, tenant_id: 'default' }),
      })
      const data = await res.json()
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: data.answer,
        sources: data.sources,
      }])
    } catch (e) {
      setMessages(prev => [...prev, { role: 'assistant', content: 'Error: could not reach Nexus AI.' }])
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { bottomRef.current?.scrollIntoView({ behavior: 'smooth' }) }, [messages])

  return (
    <div className="nexus-chat-container">
      <div className="nexus-chat-header">
        <div className="nexus-chat-title">Nexus AI</div>
        <div className="nexus-chat-subtitle">Supply Chain Intelligence</div>
      </div>

      <div className="nexus-chat-messages">
        {messages.length === 0 && (
          <div className="nexus-chat-empty">
            <div className="nexus-chat-empty-title">Ask anything about your supply chain.</div>
            <div className="nexus-chat-empty-subtitle">Powered by BCI + RAG</div>
          </div>
        )}
        {messages.map((m, i) => (
          <div key={i} className={`nexus-chat-message-row ${m.role}`}>
            <div className={`nexus-chat-bubble ${m.role}`}>
              {m.content}
              {m.sources && m.sources.length > 0 && (
                <div className="nexus-chat-sources">
                  <span className="nexus-chat-source-badge">
                    {m.sources.length} source{m.sources.length > 1 ? 's' : ''}
                  </span>
                </div>
              )}
            </div>
          </div>
        ))}
        {loading && (
          <div className="nexus-chat-message-row assistant">
            <div className="nexus-chat-bubble assistant loading">
              Nexus AI is thinking...
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      <div className="nexus-chat-input-area">
        <input
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && !e.shiftKey && send()}
          placeholder="Ask about your supply chain..."
          className="nexus-chat-input"
        />
        <button className="nexus-chat-send" onClick={send} disabled={!input.trim() || loading}>
          Send
        </button>
      </div>
    </div>
  )
}
