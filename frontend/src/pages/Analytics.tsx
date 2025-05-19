import { useEffect, useState } from 'react'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts'
import api from '../api/client'

const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444']

export default function Analytics() {
  const [data, setData] = useState<any>(null)

  useEffect(() => {
    api.get('/admin/analytics').then(({ data }) => setData(data)).catch(() => {})
  }, [])

  if (!data) return <p className="text-gray-400 text-sm">Loading...</p>

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Analytics</h1>
      <div className="grid grid-cols-2 gap-6">
        <div className="bg-white border rounded-xl p-5">
          <h2 className="text-sm font-medium text-gray-600 mb-4">Queries by Day</h2>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={data.queries_by_day}>
              <XAxis dataKey="date" tick={{ fontSize: 11 }} />
              <YAxis tick={{ fontSize: 11 }} />
              <Tooltip />
              <Bar dataKey="count" fill="#3b82f6" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
        <div className="bg-white border rounded-xl p-5">
          <h2 className="text-sm font-medium text-gray-600 mb-4">Documents by Type</h2>
          <ResponsiveContainer width="100%" height={200}>
            <PieChart>
              <Pie data={data.docs_by_type} dataKey="count" nameKey="type" cx="50%" cy="50%" outerRadius={80}>
                {data.docs_by_type.map((_: any, i: number) => (
                  <Cell key={i} fill={COLORS[i % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  )
}
