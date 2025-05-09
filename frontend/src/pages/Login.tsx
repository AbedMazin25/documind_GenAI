import { useState } from 'react'
import api from '../api/client'
import { useAuthStore } from '../store/auth'
import { useNavigate } from 'react-router-dom'

export default function Login() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const setUser = useAuthStore((s) => s.setUser)
  const navigate = useNavigate()

  const handleSubmit = async () => {
    try {
      const { data } = await api.post('/auth/login', { email, password })
      localStorage.setItem('access_token', data.access_token)
      localStorage.setItem('refresh_token', data.refresh_token)
      setUser(data.user)
      navigate('/')
    } catch {
      setError('Invalid credentials')
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="bg-white p-8 rounded-xl shadow-sm w-full max-w-sm">
        <h1 className="text-2xl font-bold mb-6">DocuMind</h1>
        {error && <p className="text-red-500 text-sm mb-4">{error}</p>}
        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          className="w-full border rounded-lg px-3 py-2 mb-3 text-sm"
        />
        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleSubmit()}
          className="w-full border rounded-lg px-3 py-2 mb-4 text-sm"
        />
        <button
          onClick={handleSubmit}
          className="w-full bg-blue-600 text-white rounded-lg py-2 text-sm font-medium"
        >
          Sign in
        </button>
      </div>
    </div>
  )
}
