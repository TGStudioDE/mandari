import React from 'react'
import { api } from '../lib/api'

type Staff = { id: number; user: number; department: string; scopes: string[]; can_create_test_env: boolean; user_detail?: any }

const SCOPE_OPTIONS = [
  { value: 'offers:create', label: 'Angebote erstellen' },
  { value: 'offers:send', label: 'Angebote versenden' },
  { value: 'test_env:create', label: 'Test-Organisationen anlegen' },
]

export function StaffPage() {
  const [items, setItems] = React.useState<Staff[]>([])
  const [userId, setUserId] = React.useState('')
  const [department, setDepartment] = React.useState('sales')
  const [scopes, setScopes] = React.useState<string[]>(['offers:create','offers:send','test_env:create'])
  const [canCreate, setCanCreate] = React.useState(true)

  const [editId, setEditId] = React.useState<number | null>(null)
  const [editDepartment, setEditDepartment] = React.useState('sales')
  const [editScopes, setEditScopes] = React.useState<string[]>([])
  const [editCanCreate, setEditCanCreate] = React.useState(true)

  async function load() {
    const res = await api('/staff/')
    setItems(res)
  }

  React.useEffect(() => { load() }, [])

  async function create(e: React.FormEvent) {
    e.preventDefault()
    const payload = { user: Number(userId), department, scopes, can_create_test_env: canCreate }
    await api('/staff/', { method: 'POST', body: JSON.stringify(payload) })
    setUserId(''); setDepartment('sales'); setScopes(['offers:create','offers:send','test_env:create']); setCanCreate(true)
    await load()
  }

  async function del(id: number) {
    if (!confirm('Mitarbeiterprofil löschen?')) return
    await api(`/staff/${id}/`, { method: 'DELETE' })
    await load()
  }

  async function createTestTenant() {
    const name = prompt('Name der Test-Organisation?', 'Test Org') || 'Test Org'
    const res = await api('/offer-drafts/create-test-org/', { method: 'POST', body: JSON.stringify({ name }) })
    alert(`Test-Organisation angelegt: ${(res as any).slug || (res as any).name}`)
  }

  function beginEdit(item: Staff) {
    setEditId(item.id)
    setEditDepartment(item.department || 'sales')
    setEditScopes(Array.isArray(item.scopes) ? item.scopes : [])
    setEditCanCreate(!!item.can_create_test_env)
  }

  function cancelEdit() {
    setEditId(null)
  }

  async function saveEdit(id: number) {
    const payload = { department: editDepartment, scopes: editScopes, can_create_test_env: editCanCreate }
    await api(`/staff/${id}/`, { method: 'PUT', body: JSON.stringify(payload) })
    setEditId(null)
    await load()
  }

  return (
    <div className="p-6">
      <h1 className="text-xl font-semibold mb-4">Team & Berechtigungen</h1>
      <div className="mb-4 flex flex-wrap gap-2">
        <button className="px-3 py-2 rounded bg-slate-800" onClick={createTestTenant}>Test-Organisation anlegen</button>
      </div>
      <form onSubmit={create} className="flex flex-wrap gap-3 mb-6 items-start">
        <input className="px-3 py-2 rounded bg-slate-800 border border-slate-700" placeholder="Nutzer-ID" value={userId} onChange={e => setUserId(e.target.value)} />
        <select className="px-3 py-2 rounded bg-slate-800 border border-slate-700" value={department} onChange={e => setDepartment(e.target.value)}>
          <option value="admin">Admin</option>
          <option value="sales">Sales</option>
          <option value="support">Support</option>
          <option value="engineering">Engineering</option>
        </select>
        <div className="grid gap-1 bg-slate-900 border border-slate-800 rounded p-2">
          <div className="text-xs text-slate-400">Funktionen</div>
          {SCOPE_OPTIONS.map(opt => (
            <label key={opt.value} className="inline-flex items-center gap-2 text-sm">
              <input
                type="checkbox"
                className="accent-blue-600"
                checked={scopes.includes(opt.value)}
                onChange={e => {
                  const next = e.target.checked ? [...scopes, opt.value] : scopes.filter(v => v !== opt.value)
                  setScopes(next)
                }}
              />
              <span>{opt.label}</span>
            </label>
          ))}
        </div>
        <label className="inline-flex items-center gap-2 text-sm">
          <input type="checkbox" className="accent-blue-600" checked={canCreate} onChange={e => setCanCreate(e.target.checked)} />
          Darf Test-Organisationen anlegen
        </label>
        <button className="px-3 py-2 rounded bg-blue-600 hover:bg-blue-500" type="submit">Hinzufügen</button>
      </form>
      <table className="w-full text-sm">
        <thead>
          <tr className="text-left text-slate-400"><th className="py-2">ID</th><th>Nutzer</th><th>Bereich</th><th>Rechte</th><th>Test-Org</th><th></th></tr>
        </thead>
        <tbody>
          {items.map(s => (
            <tr key={s.id} className="border-t border-slate-800 align-top">
              <td className="py-2">{s.id}</td>
              <td>{s.user}</td>
              <td>
                {editId === s.id ? (
                  <select className="px-2 py-1 rounded bg-slate-800 border border-slate-700" value={editDepartment} onChange={e => setEditDepartment(e.target.value)}>
                    <option value="admin">Admin</option>
                    <option value="sales">Sales</option>
                    <option value="support">Support</option>
                    <option value="engineering">Engineering</option>
                  </select>
                ) : (
                  s.department
                )}
              </td>
              <td className="font-mono text-xs text-slate-400">
                {editId === s.id ? (
                  <div className="not-italic font-normal text-slate-200 grid gap-1">
                    {SCOPE_OPTIONS.map(opt => (
                      <label key={opt.value} className="inline-flex items-center gap-2 text-sm">
                        <input
                          type="checkbox"
                          className="accent-blue-600"
                          checked={editScopes.includes(opt.value)}
                          onChange={e => {
                            const next = e.target.checked ? [...editScopes, opt.value] : editScopes.filter(v => v !== opt.value)
                            setEditScopes(next)
                          }}
                        />
                        <span>{opt.label}</span>
                      </label>
                    ))}
                  </div>
                ) : (
                  (s.scopes || []).join(', ')
                )}
              </td>
              <td>
                {editId === s.id ? (
                  <label className="inline-flex items-center gap-2 text-sm">
                    <input type="checkbox" className="accent-blue-600" checked={editCanCreate} onChange={e => setEditCanCreate(e.target.checked)} />
                    erlaubt
                  </label>
                ) : (
                  s.can_create_test_env ? 'Ja' : 'Nein'
                )}
              </td>
              <td className="whitespace-nowrap">
                {editId === s.id ? (
                  <div className="flex gap-2">
                    <button className="px-2 py-1 rounded bg-blue-600 hover:bg-blue-500" onClick={() => saveEdit(s.id)}>Speichern</button>
                    <button className="px-2 py-1 rounded bg-slate-800" onClick={cancelEdit}>Abbrechen</button>
                  </div>
                ) : (
                  <div className="flex gap-2">
                    <button className="px-2 py-1 rounded bg-slate-800" onClick={() => beginEdit(s)}>Bearbeiten</button>
                    <button className="px-2 py-1 rounded bg-slate-800" onClick={() => del(s.id)}>Entfernen</button>
                  </div>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}


