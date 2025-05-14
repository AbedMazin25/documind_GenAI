import { useEffect, useState, useRef } from 'react'
import api from '../api/client'

interface Doc { id: number; filename: string; status: string; created_at: string }

export default function Documents() {
  const [docs, setDocs] = useState<Doc[]>([])
  const fileRef = useRef<HTMLInputElement>(null)

  const load = () => api.get('/documents/').then(({ data }) => setDocs(data)).catch(() => {})
  useEffect(() => { load() }, [])

  const upload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return
    const form = new FormData()
    form.append('file', file)
    await api.post('/documents/upload', form)
    load()
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold">Documents</h1>
        <button
          onClick={() => fileRef.current?.click()}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg text-sm"
        >
          Upload
        </button>
        <input ref={fileRef} type="file" className="hidden" onChange={upload} accept=".pdf,.docx,.txt" />
      </div>
      <div className="bg-white border rounded-xl overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-gray-50 text-gray-500 text-xs uppercase">
            <tr>
              <th className="px-4 py-3 text-left">Name</th>
              <th className="px-4 py-3 text-left">Status</th>
              <th className="px-4 py-3 text-left">Uploaded</th>
            </tr>
          </thead>
          <tbody>
            {docs.map((d) => (
              <tr key={d.id} className="border-t hover:bg-gray-50">
                <td className="px-4 py-3">{d.filename}</td>
                <td className="px-4 py-3">
                  <span className={`px-2 py-0.5 rounded text-xs font-medium ${
                    d.status === 'ready' ? 'bg-green-100 text-green-700' : 'bg-yellow-100 text-yellow-700'
                  }`}>{d.status}</span>
                </td>
                <td className="px-4 py-3 text-gray-400">{new Date(d.created_at).toLocaleDateString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
