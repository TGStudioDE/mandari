import React from 'react'
import { api } from '../lib/api'

type Doc = { id: number; title: string; created_at: string }

export function SearchPage() {
  const [q, setQ] = React.useState('')
  const [items, setItems] = React.useState<Doc[]>([])
  const [loading, setLoading] = React.useState(false)

  async function runSearch(e?: React.FormEvent) {
    e?.preventDefault()
    setLoading(true)
    try {
      const data = await api(`/documents/search?q=${encodeURIComponent(q)}`)
      setItems(data.results ?? data)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <h1 className="text-xl font-semibold mb-4">Suche</h1>
      <form onSubmit={runSearch} className="flex items-center gap-2 mb-4">
        <input className="flex-1 rounded bg-slate-800 border border-slate-700 px-3 py-2" placeholder="Suchbegriff" value={q} onChange={e => setQ(e.target.value)} />
        <button className="px-4 py-2 rounded bg-brand text-white disabled:opacity-60" disabled={loading}>Suchen</button>
      </form>
      <ul className="space-y-2">
        {items.map(d => (
          <li key={d.id} className="rounded border border-slate-800 p-3 bg-slate-900/40">
            <div className="font-medium">{d.title}</div>
            <div className="text-xs text-slate-400">{d.created_at ? new Date(d.created_at).toLocaleString() : ''}</div>
          </li>
        ))}
      </ul>
    </div>
  )
}


