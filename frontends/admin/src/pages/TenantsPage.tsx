import React from 'react'
import { api } from '../lib/api'

type Tenant = { id: number; name: string; slug: string; domain: string }

export function TenantsPage() {
  const [items, setItems] = React.useState<Tenant[]>([])
  const [name, setName] = React.useState('')
  const [slug, setSlug] = React.useState('')
  const [domain, setDomain] = React.useState('')

  async function load() {
    const data = await api('/tenants/')
    setItems(data)
  }

  React.useEffect(() => { load() }, [])

  async function createTenant(e: React.FormEvent) {
    e.preventDefault()
    await api('/tenants/', { method: 'POST', body: JSON.stringify({ name, slug, domain }) })
    setName(''); setSlug(''); setDomain('')
    await load()
  }

  async function triggerSubspace(id: number) {
    await api(`/tenants/${id}/create-subspace/`, { method: 'POST' })
    alert('Subspace-Provisionierung angestoßen')
  }

  return (
    <div>
      <h1>Mandanten</h1>
      <form onSubmit={createTenant} style={{ display: 'flex', gap: 8, marginBottom: 16 }}>
        <input placeholder="Name" value={name} onChange={e => setName(e.target.value)} />
        <input placeholder="Slug" value={slug} onChange={e => setSlug(e.target.value)} />
        <input placeholder="Domain" value={domain} onChange={e => setDomain(e.target.value)} />
        <button type="submit">Anlegen</button>
      </form>
      <table>
        <thead>
          <tr><th>ID</th><th>Name</th><th>Slug</th><th>Domain</th><th>Aktionen</th></tr>
        </thead>
        <tbody>
          {items.map(t => (
            <tr key={t.id}>
              <td>{t.id}</td>
              <td>{t.name}</td>
              <td>{t.slug}</td>
              <td>{t.domain}</td>
              <td>
                <button onClick={() => triggerSubspace(t.id)}>Subspace</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}


