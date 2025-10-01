import React from 'react'
import { useSearchParams, useNavigate } from 'react-router-dom'
import { api } from '../lib/api'

export function ResetPage() {
  const [params] = useSearchParams()
  const token = params.get('token')
  const navigate = useNavigate()
  const [email, setEmail] = React.useState('')
  const [password, setPassword] = React.useState('')
  const [confirm, setConfirm] = React.useState('')
  const [message, setMessage] = React.useState<string>('')

  async function requestReset(e: React.FormEvent) {
    e.preventDefault()
    await api('/auth/password-reset-request/', { method: 'POST', body: JSON.stringify({ email }) })
    setMessage('Wenn die E-Mail existiert, wurde ein Link versendet.')
  }

  async function confirmReset(e: React.FormEvent) {
    e.preventDefault()
    if (password !== confirm) { setMessage('Passwörter stimmen nicht überein.'); return }
    await api('/auth/password-reset-confirm/', { method: 'POST', body: JSON.stringify({ token, new_password: password }) })
    setMessage('Passwort aktualisiert. Bitte einloggen...')
    setTimeout(() => navigate('/login'), 1200)
  }

  return (
    <div className="min-h-screen grid place-items-center bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 text-slate-100">
      <div className="w-full max-w-md rounded-2xl bg-slate-900/60 backdrop-blur border border-slate-700 p-8 shadow-xl">
        {!token ? (
          <form onSubmit={requestReset} className="grid gap-4">
            <div className="mb-2 text-center">
              <h1 className="text-2xl font-semibold">Passwort zurücksetzen</h1>
              <p className="text-slate-400 text-sm">Link per E-Mail anfordern</p>
            </div>
            <div>
              <label className="block text-sm mb-1">E-Mail</label>
              <input className="w-full rounded-lg bg-slate-800 border border-slate-700 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-brand-500" value={email} onChange={e => setEmail(e.target.value)} />
            </div>
            <button className="mt-2 inline-flex justify-center items-center gap-2 rounded-lg bg-brand-600 hover:bg-brand-500 px-4 py-2 font-medium">Link senden</button>
            {message && <p className="text-sm text-slate-400 text-center">{message}</p>}
          </form>
        ) : (
          <form onSubmit={confirmReset} className="grid gap-4">
            <div className="mb-2 text-center">
              <h1 className="text-2xl font-semibold">Neues Passwort</h1>
              <p className="text-slate-400 text-sm">Bitte neues Passwort setzen</p>
            </div>
            <div>
              <label className="block text-sm mb-1">Neues Passwort</label>
              <input type="password" className="w-full rounded-lg bg-slate-800 border border-slate-700 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-brand-500" value={password} onChange={e => setPassword(e.target.value)} />
            </div>
            <div>
              <label className="block text-sm mb-1">Bestätigung</label>
              <input type="password" className="w-full rounded-lg bg-slate-800 border border-slate-700 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-brand-500" value={confirm} onChange={e => setConfirm(e.target.value)} />
            </div>
            <button className="mt-2 inline-flex justify-center items-center gap-2 rounded-lg bg-brand-600 hover:bg-brand-500 px-4 py-2 font-medium">Speichern</button>
            {message && <p className="text-sm text-slate-400 text-center">{message}</p>}
          </form>
        )}
      </div>
    </div>
  )
}


