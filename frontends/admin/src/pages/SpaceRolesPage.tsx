import React from 'react'
import { api } from '../lib/api'

type Org = { id: number; name: string }
type Subspace = { id: number; tenant: number; name: string; key: string }
type Member = { id: number; org: number; user: number; role: string; user_detail?: { id: number; username: string; email: string } }
type SpaceMembership = { id: number; user: number; subspace: number; role: string }

export function SpaceRolesPage() {
  const [orgId, setOrgId] = React.useState<number | ''>('' as any)
  const [orgs, setOrgs] = React.useState<Org[]>([])
  const [subspaces, setSubspaces] = React.useState<Subspace[]>([])
  const [members, setMembers] = React.useState<Member[]>([])
  const [matrix, setMatrix] = React.useState<Record<string, SpaceMembership>>({})

  React.useEffect(() => { loadOrgs() }, [])

  async function loadOrgs() {
    const list = await api('/admin/orgs/')
    setOrgs(list)
  }
  async function loadData(id: number) {
    const [subs, mems, memberships] = await Promise.all([
      api(`/admin/orgs/${id}/subspaces/`),
      api(`/memberships?org=${id}`),
      api(`/space-memberships?org=${id}`),
    ])
    setSubspaces(subs)
    setMembers(mems)
    const map: Record<string, SpaceMembership> = {}
    ;(memberships as SpaceMembership[]).forEach(m => { map[`${m.user}:${m.subspace}`] = m })
    setMatrix(map)
  }

  async function setRole(userId: number, subspaceId: number, role: string) {
    const key = `${userId}:${subspaceId}`
    const existing = matrix[key]
    if (existing) {
      const updated = await api(`/space-memberships/${existing.id}/`, { method: 'PATCH', body: JSON.stringify({ role }) })
      setMatrix(prev => ({ ...prev, [key]: updated }))
    } else {
      const created = await api(`/space-memberships/`, { method: 'POST', body: JSON.stringify({ user: userId, subspace: subspaceId, role }) })
      setMatrix(prev => ({ ...prev, [key]: created }))
    }
  }

  function currentRole(userId: number, subspaceId: number) {
    return matrix[`${userId}:${subspaceId}`]?.role || ''
  }

  return (
    <div className="p-6">
      <h1 className="text-xl font-semibold mb-4">Space-Rollenmatrix</h1>
      <div className="flex items-center gap-2 mb-4">
        <select className="bg-slate-800 border border-slate-700 rounded px-2 py-1" value={orgId} onChange={e => { const v = Number(e.target.value); setOrgId(v); if (v) loadData(v) }}>
          <option value="">Organisation wählen</option>
          {orgs.map(o => <option key={o.id} value={o.id}>{o.name}</option>)}
        </select>
      </div>
      {orgId ? (
        <div className="overflow-auto">
          <table className="text-sm min-w-[800px]">
            <thead>
              <tr>
                <th className="text-left py-2">Mitglied</th>
                {subspaces.map(s => (<th key={s.id} className="text-left py-2">{s.name}</th>))}
              </tr>
            </thead>
            <tbody>
              {members.map(m => (
                <tr key={m.id} className="border-t border-slate-800">
                  <td className="py-2">{m.user_detail?.username || m.user}</td>
                  {subspaces.map(s => (
                    <td key={s.id} className="py-2">
                      <select className="bg-slate-800 border border-slate-700 rounded px-2 py-1" value={currentRole(m.user, s.id)} onChange={e => setRole(m.user, s.id, e.target.value)}>
                        <option value="">(keine)</option>
                        <option value="space_admin">Space Admin</option>
                        <option value="editor">Editor</option>
                        <option value="submitter">Einreicher</option>
                        <option value="reader">Leser</option>
                      </select>
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : null}
    </div>
  )
}


