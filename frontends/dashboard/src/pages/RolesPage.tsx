import React from 'react'
import { api } from '../lib/api'
import { useTenantStore } from '../stores/tenant'

type Assignment = { id: number; tenant: number; user: number; committee: number; role: string }
type Committee = { id: number; name: string }

export function RolesPage() {
  const tenantId = useTenantStore((s: { tenantId: number | null }) => s.tenantId)
  const setTenantId = useTenantStore((s: { setTenantId: (id: number | null) => void }) => s.setTenantId)
  const [userId, setUserId] = React.useState<number>(1)
  const [committeeId, setCommitteeId] = React.useState<number>(0)
  const [role, setRole] = React.useState<string>('sachkundig')
  const [assignments, setAssignments] = React.useState<Assignment[]>([])
  const [committees, setCommittees] = React.useState<Committee[]>([])

  async function load() {
    const a: Assignment[] = await api(`/role-assignments/?tenant=${tenantId}`)
    setAssignments(a)
    const c: Committee[] = await api(`/committees/?tenant=${tenantId}`)
    setCommittees(c)
  }

  React.useEffect(() => { load() }, [tenantId])

  async function add(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault()
    await api('/role-assignments/', { method: 'POST', body: JSON.stringify({ tenant: tenantId, user: userId, committee: committeeId, role }) })
    setRole('sachkundig')
    await load()
  }

  return (
    <div>
      <h1>Rollen & Gremien</h1>
      <div style={{ marginBottom: 16 }}>
        <label>Tenant</label>
        <input type="number" value={tenantId || 1} onChange={(e: React.ChangeEvent<HTMLInputElement>) => setTenantId(Number(e.target.value))} />
      </div>
      <form onSubmit={add} style={{ display: 'flex', gap: 8, marginBottom: 16 }}>
        <input type="number" placeholder="User-ID" value={userId} onChange={(e: React.ChangeEvent<HTMLInputElement>) => setUserId(Number(e.target.value))} />
        <select value={committeeId} onChange={(e: React.ChangeEvent<HTMLSelectElement>) => setCommitteeId(Number(e.target.value))}>
          <option value={0}>Gremium wählen</option>
          {committees.map((c: Committee) => <option key={c.id} value={c.id}>{c.name}</option>)}
        </select>
        <select value={role} onChange={(e: React.ChangeEvent<HTMLSelectElement>) => setRole(e.target.value)}>
          <option value="sachkundig">Sachkundige Bürger*in</option>
          <option value="ratsherr">Ratsherr/frau</option>
          <option value="bezirksvertretung">Bezirksvertretung</option>
        </select>
        <button type="submit">Zuordnen</button>
      </form>

      <table>
        <thead>
          <tr><th>ID</th><th>Tenant</th><th>User</th><th>Committee</th><th>Role</th></tr>
        </thead>
        <tbody>
          {assignments.map((a: Assignment) => (
            <tr key={a.id}>
              <td>{a.id}</td>
              <td>{a.tenant}</td>
              <td>{a.user}</td>
              <td>{a.committee}</td>
              <td>{a.role}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}


