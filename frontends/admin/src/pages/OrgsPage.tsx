import React from 'react'
import { api } from '../lib/api'
import { Link } from 'react-router-dom'

type Org = {
  id: number
  name: string
  slug: string
  domain: string
  is_active: boolean
  region: string
  mfa_required_for_admins?: boolean
}

type Plan = { id: number; code: string; name: string }

type PricingAgreement = { id: number; org: number; subspace?: number; amount_cents: number; currency: string; period: string }

type Invitation = { id: number; org: number; email: string; role: string; token: string; expires_at: string }

type Membership = { id: number; org: number; user: number; role: string; user_detail?: { id: number; username: string; email: string } }

export function OrgsPage() {
  const [orgs, setOrgs] = React.useState<Org[]>([])
  const [plans, setPlans] = React.useState<Plan[]>([])
  const [q, setQ] = React.useState('')
  const [form, setForm] = React.useState({ name: '', slug: '', domain: '', region: '' })
  const [pricingByOrg, setPricingByOrg] = React.useState<Record<number, PricingAgreement[]>>({})
  const [invitesByOrg, setInvitesByOrg] = React.useState<Record<number, Invitation[]>>({})
  const [membersByOrg, setMembersByOrg] = React.useState<Record<number, Membership[]>>({})
  const [editOrgId, setEditOrgId] = React.useState<number | null>(null)
  const [editOrg, setEditOrg] = React.useState<{ name: string; slug: string; domain: string; region: string }>({ name: '', slug: '', domain: '', region: '' })

  async function load() {
    const [orgsRes, plansRes] = await Promise.all([
      api('/admin/orgs/'),
      api('/admin/plans/'),
    ])
    setOrgs(orgsRes)
    setPlans(plansRes)
    const entriesPricing = await Promise.all((orgsRes as Org[]).map(async o => [o.id, await api(`/admin/orgs/${o.id}/pricing/`)] as const))
    const pmap: Record<number, PricingAgreement[]> = {}
    for (const [id, list] of entriesPricing) pmap[id] = list as PricingAgreement[]
    setPricingByOrg(pmap)
    const entriesInvites = await Promise.all((orgsRes as Org[]).map(async o => [o.id, await api(`/admin/orgs/${o.id}/invitations/`)] as const))
    const imap: Record<number, Invitation[]> = {}
    for (const [id, list] of entriesInvites) imap[id] = list as Invitation[]
    setInvitesByOrg(imap)
    const entriesMembers = await Promise.all((orgsRes as Org[]).map(async o => [o.id, await api(`/memberships?org=${o.id}`)] as const))
    const mmap: Record<number, Membership[]> = {}
    for (const [id, list] of entriesMembers) mmap[id] = list as Membership[]
    setMembersByOrg(mmap)
  }
  function startEditOrg(o: Org) {
    setEditOrgId(o.id)
    setEditOrg({ name: o.name || '', slug: o.slug || '', domain: o.domain || '', region: o.region || '' })
  }

  function cancelEditOrg() {
    setEditOrgId(null)
  }

  async function saveEditOrg(id: number) {
    await api(`/admin/orgs/${id}/`, { method: 'PATCH', body: JSON.stringify(editOrg) })
    setEditOrgId(null)
    await load()
  }

  async function setUserEmail(userId: number) {
    const email = prompt('Neue E-Mail?') || ''
    if (!email) return
    await api(`/users/${userId}/`, { method: 'PATCH', body: JSON.stringify({ email }) })
    await load()
  }

  async function setUserPassword(userId: number) {
    const pw = prompt('Neues Passwort (min. 8 Zeichen)?') || ''
    if (!pw || pw.length < 8) return alert('Zu kurz')
    await api(`/users/${userId}/set-password/`, { method: 'POST', body: JSON.stringify({ new_password: pw }) })
    alert('Passwort aktualisiert')
  }

  async function toggleUserActive(userId: number, current = true) {
    await api(`/users/${userId}/`, { method: 'PATCH', body: JSON.stringify({ is_active: !current }) })
    await load()
  }

  React.useEffect(() => { load() }, [])

  async function createOrg(e: React.FormEvent) {
    e.preventDefault()
    await api('/admin/orgs/', { method: 'POST', body: JSON.stringify(form) })
    setForm({ name: '', slug: '', domain: '', region: '' })
    await load()
  }

  async function toggleMfaPolicy(orgId: number, current?: boolean) {
    await api(`/admin/orgs/${orgId}/`, { method: 'PATCH', body: JSON.stringify({ mfa_required_for_admins: !current }) })
    await load()
  }

  async function setPlan(orgId: number, planId: number) {
    await api(`/admin/orgs/${orgId}/subscription/`, { method: 'POST', body: JSON.stringify({ plan_id: planId }) })
    alert('Plan gesetzt')
  }

  async function deactivate(orgId: number) {
    await api(`/admin/orgs/${orgId}/deactivate/`, { method: 'POST' })
    await load()
  }
  async function reactivate(orgId: number) {
    await api(`/admin/orgs/${orgId}/reactivate/`, { method: 'POST' })
    await load()
  }

  async function setPricing(orgId: number) {
    const amount = Number(prompt('Preis (EUR) pro Periode? z.B. 199') || '0')
    if (!amount || amount <= 0) return
    const period = (prompt('Periode? (monthly/yearly)', 'monthly') || 'monthly')
    await api(`/admin/orgs/${orgId}/pricing/`, { method: 'POST', body: JSON.stringify({ amount_cents: Math.round(amount * 100), currency: 'EUR', period }) })
    const list = await api(`/admin/orgs/${orgId}/pricing/`)
    setPricingByOrg(prev => ({ ...prev, [orgId]: list }))
  }

  async function deletePricing(orgId: number, pricingId: number) {
    await api(`/admin/orgs/${orgId}/pricing/`, { method: 'DELETE', body: JSON.stringify({ id: pricingId }) })
    const list = await api(`/admin/orgs/${orgId}/pricing/`)
    setPricingByOrg(prev => ({ ...prev, [orgId]: list }))
  }

  async function createInvite(orgId: number) {
    const email = prompt('E-Mail?') || ''
    if (!email) return
    const role = prompt('Org-Rolle? (owner/billing_admin/org_admin/auditor)', 'member') || 'member'
    await api(`/admin/orgs/${orgId}/invitations/`, { method: 'POST', body: JSON.stringify({ email, role }) })
    const list = await api(`/admin/orgs/${orgId}/invitations/`)
    setInvitesByOrg(prev => ({ ...prev, [orgId]: list }))
  }

  async function resendInvite(orgId: number, inviteId: number) {
    await api(`/admin/orgs/${orgId}/invitations/${inviteId}/resend/`, { method: 'POST' })
    alert('Einladung erneut versendet')
  }

  async function cancelInvite(orgId: number, inviteId: number) {
    await api(`/admin/orgs/${orgId}/invitations/${inviteId}/cancel/`, { method: 'POST' })
    const list = await api(`/admin/orgs/${orgId}/invitations/`)
    setInvitesByOrg(prev => ({ ...prev, [orgId]: list }))
  }

  async function changeMemberRole(orgId: number, userId: number) {
    const role = prompt('Neue Org-Rolle?', 'member') || 'member'
    await api(`/admin/orgs/${orgId}/members/${userId}/role/`, { method: 'POST', body: JSON.stringify({ role }) })
    const list = await api(`/memberships?org=${orgId}`)
    setMembersByOrg(prev => ({ ...prev, [orgId]: list }))
  }

  async function editSpaceRoles(orgId: number, member: Membership) {
    alert('Subspace-Rollenmatrix: Kommt als eigener Screen (WIP)')
  }

  const filtered = orgs.filter(o => [o.name, o.slug, o.domain].join(' ').toLowerCase().includes(q.toLowerCase()))

  return (
    <div>
      <h1 className="text-xl font-semibold mb-4">Organisationen</h1>
      <form onSubmit={createOrg} className="flex gap-2 mb-4">
        <input className="px-3 py-2 rounded bg-slate-800 border border-slate-700" placeholder="Name" value={form.name} onChange={e => setForm({ ...form, name: e.target.value })} />
        <input className="px-3 py-2 rounded bg-slate-800 border border-slate-700" placeholder="Slug" value={form.slug} onChange={e => setForm({ ...form, slug: e.target.value })} />
        <input className="px-3 py-2 rounded bg-slate-800 border border-slate-700" placeholder="Domain" value={form.domain} onChange={e => setForm({ ...form, domain: e.target.value })} />
        <input className="px-3 py-2 rounded bg-slate-800 border border-slate-700" placeholder="Region" value={form.region} onChange={e => setForm({ ...form, region: e.target.value })} />
        <button className="px-3 py-2 rounded bg-blue-600 hover:bg-blue-500" type="submit">Anlegen</button>
        <div className="flex-1" />
        <input className="px-3 py-2 rounded bg-slate-800 border border-slate-700" placeholder="Suchen..." value={q} onChange={e => setQ(e.target.value)} />
      </form>
      <table className="w-full text-sm">
        <thead>
          <tr className="text-left text-slate-400">
            <th className="py-2">ID</th>
            <th>Name</th>
            <th>Slug</th>
            <th>Domain</th>
            <th>Region</th>
            <th>Status</th>
            <th>Security</th>
            <th>Preis(e)</th>
            <th>Einladungen</th>
            <th>Mitglieder</th>
            <th>Aktionen</th>
          </tr>
        </thead>
        <tbody>
          {filtered.map(o => (
            <tr key={o.id} className="border-t border-slate-800 align-top">
              <td className="py-2">{o.id}</td>
              <td>
                {editOrgId === o.id ? (
                  <input className="px-2 py-1 rounded bg-slate-800 border border-slate-700" value={editOrg.name} onChange={e => setEditOrg({ ...editOrg, name: e.target.value })} />
                ) : (
                  <Link className="text-brand hover:underline" to={`/org?id=${o.id}`}>{o.name}</Link>
                )}
              </td>
              <td>
                {editOrgId === o.id ? (
                  <input className="px-2 py-1 rounded bg-slate-800 border border-slate-700" value={editOrg.slug} onChange={e => setEditOrg({ ...editOrg, slug: e.target.value })} />
                ) : o.slug}
              </td>
              <td>
                {editOrgId === o.id ? (
                  <input className="px-2 py-1 rounded bg-slate-800 border border-slate-700" value={editOrg.domain} onChange={e => setEditOrg({ ...editOrg, domain: e.target.value })} />
                ) : o.domain}
              </td>
              <td>
                {editOrgId === o.id ? (
                  <input className="px-2 py-1 rounded bg-slate-800 border border-slate-700" value={editOrg.region} onChange={e => setEditOrg({ ...editOrg, region: e.target.value })} />
                ) : o.region}
              </td>
              <td>{o.is_active ? 'aktiv' : 'inaktiv'}</td>
              <td>
                <div className="flex flex-col gap-2">
                  <div className="flex items-center gap-2">
                    <span>2FA für Admins</span>
                    <button className="px-2 py-1 rounded bg-slate-800" onClick={() => toggleMfaPolicy(o.id, o.mfa_required_for_admins)}>
                      {o.mfa_required_for_admins ? 'Deaktivieren' : 'Aktivieren'}
                    </button>
                  </div>
                </div>
              </td>
              <td>
                <div className="flex flex-col gap-1">
                  {(pricingByOrg[o.id] || []).map(p => (
                    <div key={p.id} className="flex items-center gap-2">
                      <span>{(p.amount_cents / 100).toFixed(2)} {p.currency} / {p.period}</span>
                      <button className="px-2 py-1 rounded bg-slate-800" onClick={() => deletePricing(o.id, p.id)}>Löschen</button>
                    </div>
                  ))}
                  <button className="px-2 py-1 rounded bg-slate-800" onClick={() => setPricing(o.id)}>Preis setzen</button>
                </div>
              </td>
              <td>
                <div className="flex flex-col gap-1">
                  {(invitesByOrg[o.id] || []).map(inv => (
                    <div key={inv.id} className="flex items-center gap-2">
                      <span>{inv.email}</span>
                      <span className="text-slate-500">{new Date(inv.expires_at).toLocaleDateString()}</span>
                      <button className="px-2 py-1 rounded bg-slate-800" onClick={() => resendInvite(o.id, inv.id)}>Resend</button>
                      <button className="px-2 py-1 rounded bg-slate-800" onClick={() => cancelInvite(o.id, inv.id)}>Cancel</button>
                    </div>
                  ))}
                  <button className="px-2 py-1 rounded bg-slate-800" onClick={() => createInvite(o.id)}>Einladen</button>
                </div>
              </td>
              <td>
                <div className="flex flex-col gap-1">
                  {(membersByOrg[o.id] || []).map(m => (
                    <div key={m.id} className="flex items-center gap-2">
                      <span>{m.user_detail?.username || m.user}</span>
                      <span className="text-slate-500">{m.user_detail?.email || ''}</span>
                      <span className="px-2 py-0.5 rounded bg-slate-800 border border-slate-700">{m.role}</span>
                      <button className="px-2 py-1 rounded bg-slate-800" onClick={() => changeMemberRole(o.id, m.user)}>Rolle ändern</button>
                      <button className="px-2 py-1 rounded bg-slate-800" onClick={() => setUserEmail(m.user)}>E-Mail ändern</button>
                      <button className="px-2 py-1 rounded bg-slate-800" onClick={() => setUserPassword(m.user)}>Passwort setzen</button>
                      <button className="px-2 py-1 rounded bg-slate-800" onClick={() => toggleUserActive(m.user, true)}>Deaktivieren</button>
                      <button className="px-2 py-1 rounded bg-slate-800" onClick={() => editSpaceRoles(o.id, m)}>Space-Rollen</button>
                    </div>
                  ))}
                </div>
              </td>
              <td className="flex flex-wrap gap-2 py-2">
                {editOrgId === o.id ? (
                  <>
                    <button className="px-2 py-1 rounded bg-blue-600 hover:bg-blue-500" onClick={() => saveEditOrg(o.id)}>Speichern</button>
                    <button className="px-2 py-1 rounded bg-slate-800" onClick={cancelEditOrg}>Abbrechen</button>
                  </>
                ) : (
                  <button className="px-2 py-1 rounded bg-slate-800" onClick={() => startEditOrg(o)}>Bearbeiten</button>
                )}
                {o.is_active ? (
                  <button className="px-2 py-1 rounded bg-slate-800" onClick={() => deactivate(o.id)}>Deaktivieren</button>
                ) : (
                  <button className="px-2 py-1 rounded bg-slate-800" onClick={() => reactivate(o.id)}>Reaktivieren</button>
                )}
                <div className="flex items-center gap-2">
                  <select className="bg-slate-800 border border-slate-700 rounded px-2 py-1" onChange={e => setPlan(o.id, Number(e.target.value))} defaultValue="">
                    <option value="" disabled>Plan wählen</option>
                    {plans.map(p => (<option key={p.id} value={p.id}>{p.name}</option>))}
                  </select>
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
