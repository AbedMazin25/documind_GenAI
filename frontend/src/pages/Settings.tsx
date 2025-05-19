import { useState } from 'react'
import { useAuthStore } from '../store/auth'
import api from '../api/client'

export default function Settings() {
  const user = useAuthStore((s) => s.user)
  const [currentPw, setCurrentPw] = useState('')
  const [newPw, setNewPw] = useState('')
  const [msg, setMsg] = useState('')

  const changePassword = async () => {
    try {
      await api.post('/users/me/change-password', { current_password: currentPw, new_password: newPw })
      setMsg('Password updated.')
      setCurrentPw('')
      setNewPw('')
    } catch {
      setMsg('Failed to update password.')
    }
  }

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Settings</h1>
      <div className="bg-white border rounded-xl p-6 max-w-md">
        <h2 className="font-medium mb-4">Account</h2>
        <p className="text-sm text-gray-500 mb-1">Email</p>
        <p className="text-sm mb-4">{user?.email}</p>
        <p className="text-sm text-gray-500 mb-1">Role</p>
        <p className="text-sm mb-6 capitalize">{user?.role}</p>
        <h2 className="font-medium mb-4">Change password</h2>
        {msg && <p className="text-sm text-blue-600 mb-3">{msg}</p>}
        <input type="password" placeholder="Current password" value={currentPw}
          onChange={(e) => setCurrentPw(e.target.value)}
          className="w-full border rounded-lg px-3 py-2 mb-3 text-sm" />
        <input type="password" placeholder="New password" value={newPw}
          onChange={(e) => setNewPw(e.target.value)}
          className="w-full border rounded-lg px-3 py-2 mb-4 text-sm" />
        <button onClick={changePassword}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg text-sm">
          Update
        </button>
      </div>
    </div>
  )
}
