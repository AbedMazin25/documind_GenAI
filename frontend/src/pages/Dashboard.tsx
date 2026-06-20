import { useEffect, useState } from 'react'
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts'
import api from '../api/client'

interface Stats {
  total_documents: number
  total_queries: number
  active_users: number
  query_trend: { date: string; count: number }[]
}

export default function Dashboard() {
  const [stats, setStats] = useState<Stats | null>(null)

  useEffect(() => {
    api.get('/admin/stats').then(({ data }) => setStats(data)).catch(() => {})
  }, [])

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Dashboard</h1>
      <div className="grid grid-cols-3 gap-4 mb-8">
        <StatCard label="Documents" value={stats?.total_documents} />
        <StatCard label="Queries" value={stats?.total_queries} />
        <StatCard label="Active Users" value={stats?.active_users} />
      </div>
      {stats?.query_trend && stats.query_trend.length > 0 && (
        <div className="bg-white border rounded-xl p-5">
          <h2 className="text-sm font-medium text-gray-600 mb-4">Query volume (30d)</h2>
          <ResponsiveContainer width="100%" height={200}>
            <LineChart data={stats.query_trend}>
              <XAxis dataKey="date" tick={{ fontSize: 11 }} />
              <YAxis tick={{ fontSize: 11 }} />
              <Tooltip />
              <Line type="monotone" dataKey="count" stroke="#3b82f6" strokeWidth={2} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  )
}

function StatCard({ label, value }: { label: string; value?: number }) {
  return (
    <div className="bg-white rounded-xl border p-5">
      <p className="text-sm text-gray-500">{label}</p>
      <p className="text-3xl font-bold mt-1">{(value ?? 0).toLocaleString()}</p>
    </div>
  )
}
