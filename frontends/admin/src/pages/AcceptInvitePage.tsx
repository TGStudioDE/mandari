import React from 'react'
import { api } from '../lib/api'

export function AcceptInvitePage() {
  const [token, setToken] = React.useState<string>('')
  const [username, setUsername] = React.useState<string>('')
  const [password, setPassword] = React.useState<string>('')
  const [status, setStatus] = React.useState<string>('')

  React.useEffect(() => {
    const params = new URLSearchParams(location.search)
    const t = params.get('token') || ''
    if (t) setToken(t)
  }, [])

  async function submit(e: React.FormEvent) {
    e.preventDefault()
    setStatus('')
    try {
      await api('/auth/accept-invite/', { method: 'POST', body: JSON.stringify({ token, username, password }) })
      setStatus('Einladung akzeptiert. Bitte einloggen.')
    } catch (e: any) {
      setStatus(e?.message || 'Fehler')
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-950 text-slate-100 p-6">
      <form onSubmit={submit} className="w-full max-w-md bg-slate-900 border border-slate-800 p-6 rounded grid gap-3">
        <h1 className="text-lg font-semibold">Einladung annehmen</h1>
        <input className="px-3 py-2 rounded bg-slate-800 border border-slate-700" placeholder="Token" value={token} onChange={e => setToken(e.target.value)} />
        <input className="px-3 py-2 rounded bg-slate-800 border border-slate-700" placeholder="Benutzername" value={username} onChange={e => setUsername(e.target.value)} />
        <input type="password" className="px-3 py-2 rounded bg-slate-800 border border-slate-700" placeholder="Passwort" value={password} onChange={e => setPassword(e.target.value)} />
        <button className="px-3 py-2 rounded bg-blue-600 hover:bg-blue-500" type="submit">Bestätigen</button>
        {status ? <div className="text-sm text-slate-300">{status}</div> : null}
      </form>
    </div>
  )
}


