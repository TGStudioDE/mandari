import React from 'react'
import { api } from '../lib/api'

type Motion = { id: number; title: string; status: string; updated_at: string }

export function MyMotionsPage() {
  const [items, setItems] = React.useState<Motion[]>([])
  React.useEffect(() => { (async () => {
    const data = await api('/motions/')
    setItems(data)
  })() }, [])
  return (
    <div>
      <h1 className="text-xl font-semibold mb-4">Meine Anträge</h1>
      <ul className="space-y-2">
        {items.map(m => (
          <li key={m.id} className="rounded border border-slate-800 p-3 bg-slate-900/40">
            <div className="font-medium">{m.title}</div>
            <div className="text-xs text-slate-400">{m.status} · {new Date(m.updated_at).toLocaleString()}</div>
          </li>
        ))}
      </ul>
    </div>
  )
}


