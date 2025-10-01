import React from 'react'
import { api } from '../lib/api'

type Lead = { id: number; company?: string; name: string; email: string; message?: string; confirmed_at?: string }
type Offer = { id: number; lead?: number; org?: number; title: string; customer_email: string; amount_cents?: number; status: string; next_step?: string; due_date?: string }

export function CrmPage() {
  const [leads, setLeads] = React.useState<Lead[]>([])
  const [offers, setOffers] = React.useState<Offer[]>([])
  const [filter, setFilter] = React.useState({ q: '', status: '' })
  const [draft, setDraft] = React.useState<Offer>({ id: 0 as any, title: '', customer_email: '', status: 'draft' })
  const [leadDraft, setLeadDraft] = React.useState<Lead>({ id: 0 as any, name: '', email: '' as any })
  const [editingLeadId, setEditingLeadId] = React.useState<number | null>(null)

  async function load() {
    const [ls, os] = await Promise.all([
      api('/leads/'),
      api('/offer-drafts/'),
    ])
    setLeads(ls)
    setOffers(os)
  }

  React.useEffect(() => { load() }, [])

  async function createOffer(e: React.FormEvent) {
    e.preventDefault()
    await api('/offer-drafts/', { method: 'POST', body: JSON.stringify(draft) })
    setDraft({ id: 0 as any, title: '', customer_email: '', status: 'draft' })
    await load()
  }

  async function createLead(e: React.FormEvent) {
    e.preventDefault()
    await api('/leads/', { method: 'POST', body: JSON.stringify(leadDraft) })
    setLeadDraft({ id: 0 as any, name: '' as any, email: '' as any })
    await load()
  }

  function startEditLead(lead: Lead) {
    setEditingLeadId(lead.id)
    setLeadDraft({ id: lead.id, name: lead.name as any, email: lead.email as any, company: lead.company, message: lead.message })
  }

  async function saveLead() {
    if (!editingLeadId) return
    await api(`/leads/${editingLeadId}/`, { method: 'PATCH', body: JSON.stringify(leadDraft) })
    setEditingLeadId(null)
    setLeadDraft({ id: 0 as any, name: '' as any, email: '' as any })
    await load()
  }

  async function deleteLead(id: number) {
    if (!confirm('Lead löschen?')) return
    await api(`/leads/${id}/`, { method: 'DELETE' })
    await load()
  }

  const filteredLeads = leads.filter(l => {
    const q = filter.q.toLowerCase()
    return [l.company, l.name, l.email, l.message].join(' ').toLowerCase().includes(q)
  })
  const filteredOffers = offers.filter(o => (filter.status ? o.status === filter.status : true))

  return (
    <div className="p-6 grid gap-6">
      <h1 className="text-xl font-semibold">CRM</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <section className="bg-slate-900 border border-slate-800 rounded p-4">
          <div className="flex items-center justify-between mb-3">
            <h2 className="font-semibold">Leads</h2>
            <input className="px-3 py-2 rounded bg-slate-800 border border-slate-700" placeholder="Suche" value={filter.q} onChange={e => setFilter({ ...filter, q: e.target.value })} />
          </div>
          <form onSubmit={editingLeadId ? (e => { e.preventDefault(); saveLead() }) : createLead} className="grid gap-2 mb-3">
            <div className="grid md:grid-cols-2 gap-2">
              <input className="px-3 py-2 rounded bg-slate-800 border border-slate-700" placeholder="Name" value={leadDraft.name as any} onChange={e => setLeadDraft({ ...leadDraft, name: e.target.value as any })} />
              <input className="px-3 py-2 rounded bg-slate-800 border border-slate-700" placeholder="E-Mail" value={leadDraft.email as any} onChange={e => setLeadDraft({ ...leadDraft, email: e.target.value as any })} />
            </div>
            <div className="grid md:grid-cols-2 gap-2">
              <input className="px-3 py-2 rounded bg-slate-800 border border-slate-700" placeholder="Firma" value={leadDraft.company || ''} onChange={e => setLeadDraft({ ...leadDraft, company: e.target.value })} />
              <input className="px-3 py-2 rounded bg-slate-800 border border-slate-700" placeholder="Notiz" value={leadDraft.message || ''} onChange={e => setLeadDraft({ ...leadDraft, message: e.target.value })} />
            </div>
            <div className="flex gap-2">
              {editingLeadId ? (
                <>
                  <button className="px-3 py-2 rounded bg-blue-600 hover:bg-blue-500" type="submit">Lead speichern</button>
                  <button className="px-3 py-2 rounded bg-slate-800" type="button" onClick={() => { setEditingLeadId(null); setLeadDraft({ id: 0 as any, name: '' as any, email: '' as any }) }}>Abbrechen</button>
                </>
              ) : (
                <button className="px-3 py-2 rounded bg-slate-800" type="submit">Lead anlegen</button>
              )}
            </div>
          </form>
          <div className="max-h-[360px] overflow-auto">
            <table className="w-full text-sm">
              <thead><tr className="text-left text-slate-400"><th className="py-2">Name</th><th>Email</th><th>Firma</th><th></th></tr></thead>
              <tbody>
                {filteredLeads.map(l => (
                  <tr key={l.id} className="border-t border-slate-800">
                    <td className="py-2">{l.name}</td>
                    <td>{l.email}</td>
                    <td>{l.company || ''}</td>
                    <td className="flex gap-2">
                      <button className="px-2 py-1 rounded bg-slate-800" onClick={() => setDraft({ ...draft, lead: l.id, customer_email: l.email, title: `Angebot für ${l.name}` })}>Angebot</button>
                      <button className="px-2 py-1 rounded bg-slate-800" onClick={() => startEditLead(l)}>Bearbeiten</button>
                      <button className="px-2 py-1 rounded bg-slate-800" onClick={() => deleteLead(l.id)}>Löschen</button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
        <section className="bg-slate-900 border border-slate-800 rounded p-4">
          <h2 className="font-semibold mb-2">Angebotsentwurf</h2>
          <form onSubmit={createOffer} className="grid gap-2">
            <input className="px-3 py-2 rounded bg-slate-800 border border-slate-700" placeholder="Lead ID (optional)" value={draft.lead || ''} onChange={e => setDraft({ ...draft, lead: Number(e.target.value) || undefined })} />
            <input className="px-3 py-2 rounded bg-slate-800 border border-slate-700" placeholder="Titel" value={draft.title} onChange={e => setDraft({ ...draft, title: e.target.value })} />
            <input className="px-3 py-2 rounded bg-slate-800 border border-slate-700" placeholder="Kunden E-Mail" value={draft.customer_email} onChange={e => setDraft({ ...draft, customer_email: e.target.value })} />
            <input type="number" className="px-3 py-2 rounded bg-slate-800 border border-slate-700" placeholder="Betrag (EUR)" value={draft.amount_cents || ''} onChange={e => setDraft({ ...draft, amount_cents: Number(e.target.value) * 100 })} />
            <input className="px-3 py-2 rounded bg-slate-800 border border-slate-700" placeholder="Nächster Schritt" value={draft.next_step || ''} onChange={e => setDraft({ ...draft, next_step: e.target.value })} />
            <input type="date" className="px-3 py-2 rounded bg-slate-800 border border-slate-700" value={draft.due_date || ''} onChange={e => setDraft({ ...draft, due_date: e.target.value })} />
            <button className="px-3 py-2 rounded bg-blue-600 hover:bg-blue-500" type="submit">Angebot speichern</button>
          </form>
        </section>
      </div>
      <section className="bg-slate-900 border border-slate-800 rounded p-4">
        <div className="flex items-center justify-between mb-3">
          <h2 className="font-semibold">Angebote</h2>
          <select className="px-2 py-1 rounded bg-slate-800 border border-slate-700" value={filter.status} onChange={e => setFilter({ ...filter, status: e.target.value })}>
            <option value="">Alle</option>
            <option value="draft">Draft</option>
            <option value="sent">Sent</option>
            <option value="accepted">Accepted</option>
            <option value="rejected">Rejected</option>
            <option value="lost">Lost</option>
          </select>
        </div>
        <div className="overflow-auto">
          <table className="w-full text-sm">
            <thead><tr className="text-left text-slate-400"><th className="py-2">Titel</th><th>Lead</th><th>Email</th><th>Status</th><th>Betrag</th><th>Fällig</th><th>Aktionen</th></tr></thead>
            <tbody>
              {filteredOffers.map(o => (
                <tr key={o.id} className="border-t border-slate-800">
                  <td className="py-2">{o.title}</td>
                  <td>{o.lead || '-'}</td>
                  <td>{o.customer_email}</td>
                  <td>
                    <select className="px-2 py-1 rounded bg-slate-800 border border-slate-700" value={o.status} onChange={async e => { await api(`/offer-drafts/${o.id}/`, { method: 'PATCH', body: JSON.stringify({ status: e.target.value }) }); await load() }}>
                      <option value="draft">Draft</option>
                      <option value="sent">Sent</option>
                      <option value="accepted">Accepted</option>
                      <option value="rejected">Rejected</option>
                      <option value="lost">Lost</option>
                    </select>
                  </td>
                  <td>{o.amount_cents ? (o.amount_cents/100).toFixed(2) + ' €' : '-'}</td>
                  <td>{o.due_date || '-'}</td>
                  <td className="flex gap-2">
                    <button className="px-2 py-1 rounded bg-slate-800" onClick={async () => {
                      const org = Number(prompt('Organisation ID zuordnen?') || '')
                      if (!org) return
                      await api(`/offer-drafts/${o.id}/`, { method: 'PATCH', body: JSON.stringify({ org }) })
                      await load()
                    }}>Org setzen</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  )
}


