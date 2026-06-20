import { useEffect, useState, useCallback } from 'react'
import api from '../api/client'

interface Doc { id: string; filename: string; status: string; chunk_count: number; created_at: string | null }

export default function Documents() {
  const [docs, setDocs] = useState<Doc[]>([])
  const [dragging, setDragging] = useState(false)
  const [error, setError] = useState('')

  const load = () =>
    api.get('/documents/').then(({ data }) => setDocs(data)).catch(() => setDocs([]))
  useEffect(() => { load() }, [])

  const upload = async (file: File) => {
    setError('')
    const form = new FormData()
    form.append('file', file)
    try {
      await api.post('/documents/', form)
      load()
    } catch {
      setError(`Failed to upload ${file.name}`)
    }
  }

  const onDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setDragging(false)
    const file = e.dataTransfer.files[0]
    if (file) upload(file)
  }, [])

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Documents</h1>
      {error && <p className="text-red-500 text-sm mb-4">{error}</p>}
      <div
        onDragOver={(e) => { e.preventDefault(); setDragging(true) }}
        onDragLeave={() => setDragging(false)}
        onDrop={onDrop}
        className={`border-2 border-dashed rounded-xl p-8 text-center mb-6 transition-colors ${
          dragging ? 'border-blue-400 bg-blue-50' : 'border-gray-200'
        }`}
      >
        <p className="text-gray-400 text-sm">Drag & drop PDF, DOCX, or TXT files here</p>
        <label className="mt-3 inline-block cursor-pointer text-blue-600 text-sm underline">
          or browse
          <input type="file" className="hidden" accept=".pdf,.docx,.txt"
            onChange={(e) => e.target.files?.[0] && upload(e.target.files[0])} />
        </label>
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
                    d.status === 'indexed'
                      ? 'bg-green-100 text-green-700'
                      : d.status === 'failed'
                      ? 'bg-red-100 text-red-700'
                      : 'bg-yellow-100 text-yellow-700'
                  }`}>{d.status}</span>
                </td>
                <td className="px-4 py-3 text-gray-400">
                  {d.created_at ? new Date(d.created_at).toLocaleDateString() : '—'}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
