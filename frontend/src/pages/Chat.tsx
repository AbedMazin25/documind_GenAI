import { useState, useEffect, useRef } from 'react'

interface Message { role: 'user' | 'assistant'; content: string }

export default function Chat() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [streaming, setStreaming] = useState(false)
  const [status, setStatus] = useState('')
  const wsRef = useRef<WebSocket | null>(null)
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const token = localStorage.getItem('access_token')
    const ws = new WebSocket(`ws://localhost:8000/api/v1/ws/query?token=${token}`)
    ws.onmessage = (e) => {
      const { type, content } = JSON.parse(e.data)
      if (type === 'token') {
        setStatus('')
        setMessages((prev) => {
          const last = prev[prev.length - 1]
          if (last?.role === 'assistant') {
            return [...prev.slice(0, -1), { ...last, content: last.content + content }]
          }
          return [...prev, { role: 'assistant', content }]
        })
      } else if (type === 'status') {
        setStatus('Thinking...')
      } else if (type === 'done') {
        setStreaming(false)
        setStatus('')
      }
    }
    wsRef.current = ws
    return () => ws.close()
  }, [])

  useEffect(() => { bottomRef.current?.scrollIntoView({ behavior: 'smooth' }) }, [messages])

  const send = () => {
    if (!input.trim() || streaming) return
    setMessages((m) => [...m, { role: 'user', content: input }])
    wsRef.current?.send(JSON.stringify({ query: input }))
    setInput('')
    setStreaming(true)
    setStatus('Thinking...')
  }

  return (
    <div className="flex flex-col h-full">
      <h1 className="text-2xl font-bold mb-4">Chat</h1>
      <div className="flex-1 overflow-y-auto space-y-4 mb-4">
        {messages.map((m, i) => (
          <div key={i} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-xl px-4 py-3 rounded-xl text-sm ${
              m.role === 'user' ? 'bg-blue-600 text-white' : 'bg-white border'
            }`}>{m.content}</div>
          </div>
        ))}
        {streaming && (
          <div className="text-gray-400 text-sm animate-pulse">{status || 'Generating...'}</div>
        )}
        <div ref={bottomRef} />
      </div>
      <div className="flex gap-2">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && send()}
          placeholder="Ask about your documents..."
          className="flex-1 border rounded-lg px-4 py-2 text-sm"
        />
        <button onClick={send} disabled={streaming}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg text-sm disabled:opacity-50">
          Send
        </button>
      </div>
    </div>
  )
}
