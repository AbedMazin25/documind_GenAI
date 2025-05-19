import { useState } from 'react'
import api from '../api/client'

interface Message { role: 'user' | 'assistant'; content: string }

export default function Chat() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)

  const send = async () => {
    if (!input.trim()) return
    const userMsg: Message = { role: 'user', content: input }
    setMessages((m) => [...m, userMsg])
    setInput('')
    setLoading(true)
    try {
      const { data } = await api.post('/queries/', { query: input })
      setMessages((m) => [...m, { role: 'assistant', content: data.answer }])
    } finally {
      setLoading(false)
    }
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
        {loading && <div className="text-gray-400 text-sm">Thinking...</div>}
      </div>
      <div className="flex gap-2">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && send()}
          placeholder="Ask a question about your documents..."
          className="flex-1 border rounded-lg px-4 py-2 text-sm"
        />
        <button onClick={send} className="bg-blue-600 text-white px-4 py-2 rounded-lg text-sm">Send</button>
      </div>
    </div>
  )
}
