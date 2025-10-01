import React from 'react'
import { api } from '../lib/api'

export function SettingsPage() {
  const [orgId, setOrgId] = React.useState('')
  const [apiKeyName, setApiKeyName] = React.useState('')
  const [apiKeyToken, setApiKeyToken] = React.useState('')
  const [webhookUrl, setWebhookUrl] = React.useState('')
  const [webhookEvents, setWebhookEvents] = React.useState('org.created,space.created')

  async function createApiKey(e: React.FormEvent) {
    e.preventDefault()
    const org = Number(orgId)
    const res = await api('/admin/api-keys/', { method: 'POST', body: JSON.stringify({ org, name: apiKeyName, token: cryptoRandom() }) })
    setApiKeyToken((res as any).token || '(wird einmalig angezeigt)')
  }

  async function createWebhook(e: React.FormEvent) {
    e.preventDefault()
    const org = Number(orgId)
    const events = webhookEvents.split(',').map(s => s.trim()).filter(Boolean)
    await api('/admin/webhooks/', { method: 'POST', body: JSON.stringify({ org, url: webhookUrl, secret: cryptoRandom(16), events }) })
    alert('Webhook angelegt')
  }

  return (
    <div className="p-6 grid gap-6">
      <h1 className="text-xl font-semibold">Anbindungen & Automatisierung</h1>
      <p className="text-sm text-slate-400">
        Hier richten Sie Schlüssel und Benachrichtigungen ein, damit andere Systeme sich verbinden
        können oder Sie automatisch informiert werden.
      </p>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <section className="bg-slate-900 border border-slate-800 rounded p-4 grid gap-2">
          <h2 className="font-semibold">Zugriffsschlüssel</h2>
          <p className="text-sm text-slate-400">
            Mit einem Zugriffsschlüssel darf eine Organisation Daten lesen oder schreiben.
          </p>
          <form onSubmit={createApiKey} className="grid gap-2">
            <label className="text-sm text-slate-300">Organisations-ID</label>
            <input className="px-3 py-2 rounded bg-slate-800 border border-slate-700" placeholder="z. B. 12" value={orgId} onChange={e => setOrgId(e.target.value)} />
            <label className="text-sm text-slate-300">Name des Schlüssels</label>
            <input className="px-3 py-2 rounded bg-slate-800 border border-slate-700" placeholder="z. B. Interne Anwendung" value={apiKeyName} onChange={e => setApiKeyName(e.target.value)} />
            <button className="px-3 py-2 rounded bg-blue-600 hover:bg-blue-500" type="submit">Schlüssel erstellen</button>
            {apiKeyToken ? (
              <div className="text-sm text-slate-400">
                Schlüssel: <span className="font-mono">{apiKeyToken}</span>
                <div>Hinweis: Der Schlüssel wird nur einmal angezeigt. Bitte sicher speichern.</div>
              </div>
            ) : null}
          </form>
        </section>
        <section className="bg-slate-900 border border-slate-800 rounded p-4 grid gap-2">
          <h2 className="font-semibold">Benachrichtigungen</h2>
          <p className="text-sm text-slate-400">
            Wir informieren Ihre Ziel-URL, wenn etwas Wichtiges passiert (z. B. neue Organisationen oder Räume).
          </p>
          <form onSubmit={createWebhook} className="grid gap-2">
            <label className="text-sm text-slate-300">Organisations-ID</label>
            <input className="px-3 py-2 rounded bg-slate-800 border border-slate-700" placeholder="z. B. 12" value={orgId} onChange={e => setOrgId(e.target.value)} />
            <label className="text-sm text-slate-300">Ziel-URL</label>
            <input className="px-3 py-2 rounded bg-slate-800 border border-slate-700" placeholder="https://example.org/hook" value={webhookUrl} onChange={e => setWebhookUrl(e.target.value)} />
            <label className="text-sm text-slate-300">Ereignisse</label>
            <input className="px-3 py-2 rounded bg-slate-800 border border-slate-700" placeholder="z. B. org.created, space.created" value={webhookEvents} onChange={e => setWebhookEvents(e.target.value)} />
            <p className="text-sm text-slate-400">Mehrere Ereignisse bitte mit Komma trennen.</p>
            <button className="px-3 py-2 rounded bg-blue-600 hover:bg-blue-500" type="submit">Benachrichtigung anlegen</button>
          </form>
        </section>
      </div>
    </div>
  )
}

function cryptoRandom(len = 8) {
  const arr = new Uint8Array(len)
  crypto.getRandomValues(arr)
  return Array.from(arr).map(b => b.toString(16).padStart(2, '0')).join('')
}


