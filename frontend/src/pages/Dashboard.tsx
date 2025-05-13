import { useEffect, useState } from 'react'
import api from '../api/client'

interface Stats { total_documents: number; total_queries: number; active_users: number }

export default function Dashboard() {
  const [stats, setStats] = useState<Stats | null>(null)

  useEffect(() => {
    api.get('/admin/stats').then(({ data }) => setStats(data)).catch(() => {})
  }, [])

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Dashboard</h1>
      <div className="grid grid-cols-3 gap-4">
        {stats ? (
          <>
            <StatCard label="Documents" value={stats.total_documents} />
            <StatCard label="Queries" value={stats.total_queries} />
            <StatCard label="Active Users" value={stats.active_users} />
          </>
        ) : (
          <p className="text-gray-400 text-sm">Loading...</p>
        )}
      </div>
    </div>
  )
}

function StatCard({ label, value }: { label: string; value: number }) {
  return (
    <div className="bg-white rounded-xl border p-5">
      <p className="text-sm text-gray-500">{label}</p>
      <p className="text-3xl font-bold mt-1">{value.toLocaleString()}</p>
    </div>
  )
}
