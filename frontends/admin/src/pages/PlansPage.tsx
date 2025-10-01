import React from 'react'
import { api } from '../lib/api'

type Plan = { id: number; code: string; name: string; features_json: Record<string, any>; hard_limits_json?: Record<string, any>; soft_limits_json?: Record<string, any> }

const FEATURE_OPTIONS = [
  { key: 'public_portal', label: 'Öffentliches Portal' },
  { key: 'signing', label: 'Digitales Signieren' },
  { key: 'analytics', label: 'Analytics' },
  { key: 'priority_support', label: 'Priorisierter Support' },
]

export function PlansPage() {
  const [plans, setPlans] = React.useState<Plan[]>([])
  const [code, setCode] = React.useState('')
  const [name, setName] = React.useState('')
  const [features, setFeatures] = React.useState('{"public_portal": true}')
  const [featureToggles, setFeatureToggles] = React.useState<Record<string, boolean>>({ public_portal: true, signing: false })
  const [customFeatureKey, setCustomFeatureKey] = React.useState('')
  const [hardLimits, setHardLimits] = React.useState<{ max_users: number | '' ; max_storage_gb: number | '' }>({ max_users: '', max_storage_gb: '' })
  const [softLimits, setSoftLimits] = React.useState<{ api_rate_limit: number | '' }>({ api_rate_limit: '' })

  const [editId, setEditId] = React.useState<number | null>(null)
  const [editCode, setEditCode] = React.useState('')
  const [editName, setEditName] = React.useState('')
  const [editFeatures, setEditFeatures] = React.useState<Record<string, boolean>>({})
  const [editHardLimits, setEditHardLimits] = React.useState<{ max_users: number | '' ; max_storage_gb: number | '' }>({ max_users: '', max_storage_gb: '' })
  const [editSoftLimits, setEditSoftLimits] = React.useState<{ api_rate_limit: number | '' }>({ api_rate_limit: '' })

  async function load() {
    const res = await api('/admin/plans/')
    setPlans(res)
  }

  React.useEffect(() => { load() }, [])

  async function create(e: React.FormEvent) {
    e.preventDefault()
    let features_json: any = {}
    try { features_json = JSON.parse(features) } catch {}
    features_json = { ...features_json, ...featureToggles }
    const hard_limits_json: Record<string, any> = {}
    if (hardLimits.max_users !== '' && !Number.isNaN(Number(hardLimits.max_users))) hard_limits_json.max_users = Number(hardLimits.max_users)
    if (hardLimits.max_storage_gb !== '' && !Number.isNaN(Number(hardLimits.max_storage_gb))) hard_limits_json.max_storage_gb = Number(hardLimits.max_storage_gb)
    const soft_limits_json: Record<string, any> = {}
    if (softLimits.api_rate_limit !== '' && !Number.isNaN(Number(softLimits.api_rate_limit))) soft_limits_json.api_rate_limit = Number(softLimits.api_rate_limit)
    await api('/admin/plans/', { method: 'POST', body: JSON.stringify({ code, name, features_json, hard_limits_json, soft_limits_json }) })
    setCode(''); setName(''); setFeatures('{"public_portal": true}'); setFeatureToggles({ public_portal: true, signing: false }); setCustomFeatureKey(''); setHardLimits({ max_users: '', max_storage_gb: '' }); setSoftLimits({ api_rate_limit: '' })
    await load()
  }

  async function del(id: number) {
    if (!confirm('Plan löschen?')) return
    await api(`/admin/plans/${id}/`, { method: 'DELETE' })
    await load()
  }

  function beginEdit(p: Plan) {
    setEditId(p.id)
    setEditCode(p.code)
    setEditName(p.name)
    const f = p.features_json || {}
    setEditFeatures({
      public_portal: !!f.public_portal,
      signing: !!f.signing,
      analytics: !!f.analytics,
      priority_support: !!f.priority_support,
      ...Object.fromEntries(Object.entries(f).filter(([k, v]) => typeof v === 'boolean' && !(FEATURE_OPTIONS.map(o => o.key).includes(k))))
    })
    const h = p.hard_limits_json || {}
    setEditHardLimits({ max_users: typeof h.max_users === 'number' ? h.max_users : '', max_storage_gb: typeof h.max_storage_gb === 'number' ? h.max_storage_gb : '' })
    const s = p.soft_limits_json || {}
    setEditSoftLimits({ api_rate_limit: typeof s.api_rate_limit === 'number' ? s.api_rate_limit : '' })
  }

  function cancelEdit() {
    setEditId(null)
  }

  async function saveEdit(id: number) {
    const payload = {
      code: editCode,
      name: editName,
      features_json: { ...editFeatures },
      hard_limits_json: {
        ...(editHardLimits.max_users !== '' ? { max_users: Number(editHardLimits.max_users) } : {}),
        ...(editHardLimits.max_storage_gb !== '' ? { max_storage_gb: Number(editHardLimits.max_storage_gb) } : {}),
      },
      soft_limits_json: {
        ...(editSoftLimits.api_rate_limit !== '' ? { api_rate_limit: Number(editSoftLimits.api_rate_limit) } : {}),
      }
    }
    await api(`/admin/plans/${id}/`, { method: 'PUT', body: JSON.stringify(payload) })
    setEditId(null)
    await load()
  }

  return (
    <div className="p-6 grid gap-6">
      <div>
        <h1 className="text-xl font-semibold mb-2">Produkte & Preise</h1>
        <p className="text-sm text-slate-400">Verwalten Sie Ihre Produktpläne. Features können bequem per Schalter aktiviert werden.</p>
      </div>
      <form onSubmit={create} className="grid gap-4 bg-slate-900 border border-slate-800 rounded p-4">
        <div className="grid gap-2 md:grid-cols-2">
          <input className="px-3 py-2 rounded bg-slate-800 border border-slate-700" placeholder="Code" value={code} onChange={e => setCode(e.target.value)} />
          <input className="px-3 py-2 rounded bg-slate-800 border border-slate-700" placeholder="Name" value={name} onChange={e => setName(e.target.value)} />
        </div>
        <div className="grid gap-3">
          <div className="text-xs text-slate-400">Features (Schalter)</div>
          <div className="flex flex-wrap gap-4">
            {FEATURE_OPTIONS.map(opt => (
              <label key={opt.key} className="inline-flex items-center gap-2 text-sm">
                <input
                  type="checkbox"
                  className="accent-blue-600"
                  checked={!!featureToggles[opt.key]}
                  onChange={e => setFeatureToggles(prev => ({ ...prev, [opt.key]: e.target.checked }))}
                />
                <span>{opt.label}</span>
              </label>
            ))}
          </div>
          <div className="flex items-center gap-2">
            <input className="px-3 py-2 rounded bg-slate-800 border border-slate-700" placeholder="Eigenes Feature (key)" value={customFeatureKey} onChange={e => setCustomFeatureKey(e.target.value)} />
            <button type="button" className="px-3 py-2 rounded bg-slate-800" onClick={() => {
              const key = customFeatureKey.trim()
              if (!key) return
              setFeatureToggles(prev => ({ ...prev, [key]: true }))
              setCustomFeatureKey('')
            }}>Feature hinzufügen</button>
          </div>
          <div className="grid gap-1">
            <label className="text-xs text-slate-400">Erweiterte Features (JSON, optional)</label>
            <input className="px-3 py-2 rounded bg-slate-800 border border-slate-700" placeholder='{"public_portal": true}' value={features} onChange={e => setFeatures(e.target.value)} />
          </div>
        </div>
        <div className="grid gap-2 md:grid-cols-2">
          <div className="grid gap-2">
            <div className="text-xs text-slate-400">Hard Limits</div>
            <div className="grid gap-2">
              <input className="px-3 py-2 rounded bg-slate-800 border border-slate-700" type="number" min={0} placeholder="Max. Nutzer (z. B. 100)" value={hardLimits.max_users}
                onChange={e => setHardLimits(prev => ({ ...prev, max_users: e.target.value === '' ? '' : Number(e.target.value) }))} />
              <input className="px-3 py-2 rounded bg-slate-800 border border-slate-700" type="number" min={0} placeholder="Max. Speicher (GB)" value={hardLimits.max_storage_gb}
                onChange={e => setHardLimits(prev => ({ ...prev, max_storage_gb: e.target.value === '' ? '' : Number(e.target.value) }))} />
            </div>
          </div>
          <div className="grid gap-2">
            <div className="text-xs text-slate-400">Soft Limits</div>
            <div className="grid gap-2">
              <input className="px-3 py-2 rounded bg-slate-800 border border-slate-700" type="number" min={0} placeholder="API Rate Limit (req/min)" value={softLimits.api_rate_limit}
                onChange={e => setSoftLimits(prev => ({ ...prev, api_rate_limit: e.target.value === '' ? '' : Number(e.target.value) }))} />
            </div>
          </div>
        </div>
        <div className="flex gap-2">
          <button className="px-3 py-2 rounded bg-blue-600 hover:bg-blue-500" type="submit">Plan anlegen</button>
        </div>
      </form>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {plans.map(p => {
          const f = p.features_json || {}
          const h = p.hard_limits_json || {}
          const s = p.soft_limits_json || {}
          const isEditing = editId === p.id
          return (
            <div key={p.id} className="bg-slate-900 border border-slate-800 rounded p-4 grid gap-3">
              <div className="flex items-start justify-between gap-3">
                {isEditing ? (
                  <input className="px-2 py-1 rounded bg-slate-800 border border-slate-700" value={editName} onChange={e => setEditName(e.target.value)} />
                ) : (
                  <h3 className="font-semibold">{p.name}</h3>
                )}
                <span className="text-xs text-slate-400">#{p.id}</span>
              </div>
              <div className="text-sm text-slate-300">
                <span className="text-slate-400 mr-2">Code:</span>
                {isEditing ? (
                  <input className="px-2 py-1 rounded bg-slate-800 border border-slate-700" value={editCode} onChange={e => setEditCode(e.target.value)} />
                ) : (
                  <span className="font-mono text-xs bg-slate-800 px-2 py-0.5 rounded border border-slate-700">{p.code}</span>
                )}
              </div>
              <div className="grid gap-2">
                <div className="text-xs text-slate-400">Features</div>
                {isEditing ? (
                  <div className="flex flex-wrap gap-3">
                    {FEATURE_OPTIONS.map(opt => (
                      <label key={opt.key} className="inline-flex items-center gap-2 text-sm">
                        <input
                          type="checkbox"
                          className="accent-blue-600"
                          checked={!!editFeatures[opt.key]}
                          onChange={e => setEditFeatures(prev => ({ ...prev, [opt.key]: e.target.checked }))}
                        />
                        <span>{opt.label}</span>
                      </label>
                    ))}
                  </div>
                ) : (
                  <div className="flex flex-wrap gap-2">
                    {Object.entries(f).filter(([_, v]) => !!v).length === 0 ? (
                      <span className="text-xs text-slate-500">Keine Features aktiv</span>
                    ) : (
                      Object.entries(f).filter(([_, v]) => !!v).map(([k]) => (
                        <span key={k} className="text-xs bg-slate-800 border border-slate-700 px-2 py-0.5 rounded">
                          {FEATURE_OPTIONS.find(o => o.key === k)?.label || k}
                        </span>
                      ))
                    )}
                  </div>
                )}
              </div>
              <div className="grid gap-2">
                <div className="text-xs text-slate-400">Limits</div>
                {isEditing ? (
                  <div className="grid gap-2">
                    <div className="grid md:grid-cols-2 gap-2">
                      <input className="px-2 py-1 rounded bg-slate-800 border border-slate-700" type="number" placeholder="Max. Nutzer" value={editHardLimits.max_users}
                        onChange={e => setEditHardLimits(prev => ({ ...prev, max_users: e.target.value === '' ? '' : Number(e.target.value) }))} />
                      <input className="px-2 py-1 rounded bg-slate-800 border border-slate-700" type="number" placeholder="Max. Speicher (GB)" value={editHardLimits.max_storage_gb}
                        onChange={e => setEditHardLimits(prev => ({ ...prev, max_storage_gb: e.target.value === '' ? '' : Number(e.target.value) }))} />
                    </div>
                    <div className="grid md:grid-cols-2 gap-2">
                      <input className="px-2 py-1 rounded bg-slate-800 border border-slate-700" type="number" placeholder="API Rate Limit (req/min)" value={editSoftLimits.api_rate_limit}
                        onChange={e => setEditSoftLimits(prev => ({ ...prev, api_rate_limit: e.target.value === '' ? '' : Number(e.target.value) }))} />
                    </div>
                  </div>
                ) : (
                  <div className="flex flex-wrap gap-2">
                    {Object.keys(h).length === 0 && Object.keys(s).length === 0 ? (
                      <span className="text-xs text-slate-500">Keine Limits gesetzt</span>
                    ) : (
                      <>
                        {typeof h.max_users === 'number' && (
                          <span className="text-xs bg-slate-800 border border-slate-700 px-2 py-0.5 rounded">Max Nutzer: {h.max_users}</span>
                        )}
                        {typeof h.max_storage_gb === 'number' && (
                          <span className="text-xs bg-slate-800 border border-slate-700 px-2 py-0.5 rounded">Max Speicher: {h.max_storage_gb} GB</span>
                        )}
                        {typeof s.api_rate_limit === 'number' && (
                          <span className="text-xs bg-slate-800 border border-slate-700 px-2 py-0.5 rounded">API Limit: {s.api_rate_limit}/min</span>
                        )}
                      </>
                    )}
                  </div>
                )}
              </div>
              <div className="flex gap-2">
                {isEditing ? (
                  <>
                    <button className="px-3 py-1.5 rounded bg-blue-600 hover:bg-blue-500" onClick={() => saveEdit(p.id)}>Speichern</button>
                    <button className="px-3 py-1.5 rounded bg-slate-800" onClick={cancelEdit}>Abbrechen</button>
                  </>
                ) : (
                  <>
                    <button className="px-3 py-1.5 rounded bg-slate-800" onClick={() => beginEdit(p)}>Bearbeiten</button>
                    <button className="px-3 py-1.5 rounded bg-slate-800" onClick={() => del(p.id)}>Löschen</button>
                  </>
                )}
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}


