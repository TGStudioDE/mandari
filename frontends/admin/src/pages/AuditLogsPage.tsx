import React from 'react'
import { api } from '../lib/api'

type Log = { id: number; org: number; actor?: number; action: string; target_type: string; target_id: string; at: string }

export function AuditLogsPage() {
  const [items, setItems] = React.useState<Log[]>([])
  const [org, setOrg] = React.useState('')
  const [actor, setActor] = React.useState('')
  const [action, setAction] = React.useState('')
  const [since, setSince] = React.useState('')

  async function load() {
    const params = new URLSearchParams()
    if (org) params.set('org', org)
    if (actor) params.set('actor', actor)
    if (action) params.set('action', action)
    if (since) params.set('since', since)
    const res = await api(`/admin/audit-logs/?${params.toString()}`)
    setItems(res)
  }

  React.useEffect(() => { load() }, [])

  return (
    <div className="p-6">
      <h1 className="text-xl font-semibold mb-4">Audit Logs</h1>
      <div className="grid grid-cols-4 gap-2 mb-4 max-w-3xl">
        <input className="px-3 py-2 rounded bg-slate-800 border border-slate-700" placeholder="Org ID" value={org} onChange={e => setOrg(e.target.value)} />
        <input className="px-3 py-2 rounded bg-slate-800 border border-slate-700" placeholder="Actor ID" value={actor} onChange={e => setActor(e.target.value)} />
        <input className="px-3 py-2 rounded bg-slate-800 border border-slate-700" placeholder="Action" value={action} onChange={e => setAction(e.target.value)} />
        <input className="px-3 py-2 rounded bg-slate-800 border border-slate-700" placeholder="Since (ISO)" value={since} onChange={e => setSince(e.target.value)} />
        <button className="px-3 py-2 rounded bg-slate-800" onClick={load}>Filtern</button>
      </div>
      <div className="overflow-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="text-left text-slate-400">
              <th className="py-2">Zeit</th>
              <th>Org</th>
              <th>Actor</th>
              <th>Action</th>
              <th>Target</th>
            </tr>
          </thead>
          <tbody>
            {items.map(x => (
              <tr key={x.id} className="border-t border-slate-800">
                <td className="py-2">{new Date(x.at).toLocaleString()}</td>
                <td>{x.org}</td>
                <td>{x.actor || ''}</td>
                <td>{x.action}</td>
                <td>{x.target_type}#{x.target_id}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}


