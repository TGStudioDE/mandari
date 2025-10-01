import React from 'react'
import { api } from '../lib/api'

type Meeting = { id: number; committee: number; start: string; end?: string }

export function AgendaPage() {
  const [items, setItems] = React.useState<Meeting[]>([])
  React.useEffect(() => { (async () => {
    const data = await api('/meetings/my-agenda/')
    setItems(data)
  })() }, [])
  return (
    <div>
      <h1 className="text-xl font-semibold mb-4">Meine Agenda</h1>
      <ul className="space-y-2">
        {items.map(m => (
          <li key={m.id} className="rounded border border-slate-800 p-3 bg-slate-900/40">
            <div className="text-sm text-slate-300">Sitzung</div>
            <div className="font-medium">{new Date(m.start).toLocaleString()}</div>
          </li>
        ))}
      </ul>
    </div>
  )
}


