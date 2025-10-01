import React from 'react'
import { api } from '../lib/api'
import { useTenantStore } from '../stores/tenant'

type Committee = { id: number; name: string }
type Meeting = { id: number; committee: number; start: string }
type Document = { id: number; title: string }

export function BrowsePage() {
  const tenantId = useTenantStore((s: { tenantId: number | null }) => s.tenantId)
  const setTenantId = useTenantStore((s: { setTenantId: (id: number | null) => void }) => s.setTenantId)
  const [committees, setCommittees] = React.useState<Committee[]>([])
  const [meetings, setMeetings] = React.useState<Meeting[]>([])
  const [documents, setDocuments] = React.useState<Document[]>([])

  React.useEffect(() => {
    (async () => {
      const c: Committee[] = await api(`/committees/?tenant=${tenantId}`)
      setCommittees(c)
      const m: Meeting[] = await api(`/meetings/?tenant=${tenantId}`)
      setMeetings(m)
      const d: Document[] = await api(`/documents/?tenant=${tenantId}`)
      setDocuments(d)
    })()
  }, [tenantId])

  return (
    <div>
      <div className="flex items-end justify-between mb-4">
        <h1 className="text-xl font-semibold">Durchsuchen</h1>
        <div className="flex items-center gap-2 text-sm">
          <label className="text-slate-400">Tenant</label>
          <input className="w-24 rounded bg-slate-800 border border-slate-700 px-2 py-1" type="number" value={tenantId || 1} onChange={(e: React.ChangeEvent<HTMLInputElement>) => setTenantId(Number(e.target.value))} />
        </div>
      </div>
      <div className="grid md:grid-cols-3 gap-4">
        <section className="rounded border border-slate-800 p-4 bg-slate-900/40">
          <h3 className="font-medium mb-2">Gremien</h3>
          <ul className="text-sm text-slate-300 space-y-1">
            {committees.map((c: Committee) => <li key={c.id}>{c.name}</li>)}
          </ul>
        </section>
        <section className="rounded border border-slate-800 p-4 bg-slate-900/40">
          <h3 className="font-medium mb-2">Sitzungen</h3>
          <ul className="text-sm text-slate-300 space-y-1">
            {meetings.map((m: Meeting) => <li key={m.id}>{new Date(m.start).toLocaleString()}</li>)}
          </ul>
        </section>
        <section className="rounded border border-slate-800 p-4 bg-slate-900/40">
          <h3 className="font-medium mb-2">Dokumente</h3>
          <ul className="text-sm text-slate-300 space-y-1">
            {documents.map((d: Document) => <li key={d.id}>{d.title}</li>)}
          </ul>
        </section>
      </div>
    </div>
  )
}


