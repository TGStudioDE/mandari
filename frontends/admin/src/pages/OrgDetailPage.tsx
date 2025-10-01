import React from 'react'
import { api } from '../lib/api'

type Org = { id: number; name: string; slug: string; domain: string; color_primary?: string; color_secondary?: string; logo_url?: string }
type Plan = { id: number; code: string; name: string; features_json?: Record<string, any>; hard_limits_json?: Record<string, any>; soft_limits_json?: Record<string, any> }

export function OrgDetailPage() {
  const [org, setOrg] = React.useState<Org | null>(null)
  const [plans, setPlans] = React.useState<Plan[]>([])
  const [branding, setBranding] = React.useState({ logo_url: '', color_primary: '#0a75ff', color_secondary: '#0f172a' })

  async function load() {
    const params = new URLSearchParams(location.search)
    const id = Number(params.get('id') || '0')
    if (!id) return
    const o = await api(`/admin/orgs/${id}/`)
    setOrg(o)
    setBranding({ logo_url: o.logo_url || '', color_primary: o.color_primary || '#0a75ff', color_secondary: o.color_secondary || '#0f172a' })
    const ps = await api('/admin/plans/')
    setPlans(ps)
  }

  React.useEffect(() => { load() }, [])

  async function saveBranding(e: React.FormEvent) {
    e.preventDefault()
    if (!org) return
    await api(`/admin/orgs/${org.id}/`, { method: 'PATCH', body: JSON.stringify(branding) })
    alert('Branding gespeichert')
    await load()
  }

  if (!org) return <div className="p-6">Organisation wird geladen…</div>

  return (
    <div className="p-6 grid gap-6">
      <h1 className="text-xl font-semibold">{org.name}</h1>
      <section className="bg-slate-900 border border-slate-800 rounded p-4 grid gap-3">
        <h2 className="font-semibold">Branding</h2>
        <form onSubmit={saveBranding} className="grid gap-2 md:grid-cols-2">
          <input className="px-3 py-2 rounded bg-slate-800 border border-slate-700" placeholder="Logo URL" value={branding.logo_url} onChange={e => setBranding({ ...branding, logo_url: e.target.value })} />
          <input className="px-3 py-2 rounded bg-slate-800 border border-slate-700" placeholder="# Primärfarbe" value={branding.color_primary} onChange={e => setBranding({ ...branding, color_primary: e.target.value })} />
          <input className="px-3 py-2 rounded bg-slate-800 border border-slate-700" placeholder="# Sekundärfarbe" value={branding.color_secondary} onChange={e => setBranding({ ...branding, color_secondary: e.target.value })} />
          <div className="flex items-center gap-2">
            <button className="px-3 py-2 rounded bg-blue-600 hover:bg-blue-500" type="submit">Speichern</button>
          </div>
        </form>
      </section>
      <section className="bg-slate-900 border border-slate-800 rounded p-4 grid gap-3">
        <h2 className="font-semibold">Verfügbare Pläne</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
          {plans.map(p => (
            <div key={p.id} className="border border-slate-800 rounded p-3 grid gap-2">
              <div className="flex items-center justify-between">
                <div>
                  <div className="font-semibold">{p.name}</div>
                  <div className="text-xs text-slate-400">{p.code}</div>
                </div>
                <span className="text-xs text-slate-400">#{p.id}</span>
              </div>
              <div className="flex flex-wrap gap-2">
                {Object.entries(p.features_json || {}).filter(([_,v]) => !!v).map(([k]) => (
                  <span key={k} className="text-xs bg-slate-800 border border-slate-700 px-2 py-0.5 rounded">{k}</span>
                ))}
              </div>
              <div className="flex flex-wrap gap-2">
                {Object.entries(p.hard_limits_json || {}).map(([k,v]) => (
                  <span key={k} className="text-xs bg-slate-800 border border-slate-700 px-2 py-0.5 rounded">{k}: {String(v)}</span>
                ))}
                {Object.entries(p.soft_limits_json || {}).map(([k,v]) => (
                  <span key={k} className="text-xs bg-slate-800 border border-slate-700 px-2 py-0.5 rounded">{k}: {String(v)}</span>
                ))}
              </div>
            </div>
          ))}
        </div>
      </section>
    </div>
  )
}



