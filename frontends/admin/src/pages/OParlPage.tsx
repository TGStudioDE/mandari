import React from 'react'
import { api } from '../lib/api'

type Source = { id: number; tenant: number; root_url: string; enabled: boolean; last_synced_at?: string }

export function OParlPage() {
  const [items, setItems] = React.useState<Source[]>([])
  const [tenant, setTenant] = React.useState<number>(1)
  const [root, setRoot] = React.useState('')

  async function load() {
    const data = await api('/oparl-sources/')
    setItems(data)
  }

  React.useEffect(() => { load() }, [])

  async function createSource(e: React.FormEvent) {
    e.preventDefault()
    await api('/oparl-sources/', { method: 'POST', body: JSON.stringify({ tenant, root_url: root, enabled: true }) })
    setRoot('')
    await load()
  }

  async function trigger(id: number) {
    await api(`/oparl-sources/${id}/trigger/`, { method: 'POST' })
    alert('Ingest ausgelöst')
  }

  return (
    <div>
      <h1>OParl</h1>
      <form onSubmit={createSource} style={{ display: 'flex', gap: 8, marginBottom: 16 }}>
        <input type="number" placeholder="Tenant ID" value={tenant} onChange={e => setTenant(Number(e.target.value))} />
        <input placeholder="Root URL" value={root} onChange={e => setRoot(e.target.value)} />
        <button type="submit">Quelle anlegen</button>
      </form>
      <table>
        <thead>
          <tr><th>ID</th><th>Tenant</th><th>Root</th><th>Enabled</th><th>Last Sync</th><th>Aktionen</th></tr>
        </thead>
        <tbody>
          {items.map(s => (
            <tr key={s.id}>
              <td>{s.id}</td>
              <td>{s.tenant}</td>
              <td>{s.root_url}</td>
              <td>{String(s.enabled)}</td>
              <td>{s.last_synced_at || '-'}</td>
              <td><button onClick={() => trigger(s.id)}>Trigger</button></td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}


