import React from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '../stores/auth'

export function LoginPage() {
  const [username, setUsername] = React.useState('')
  const [password, setPassword] = React.useState('')
  const login = useAuthStore(s => s.login)
  const loading = useAuthStore(s => s.loading)
  const error = useAuthStore(s => s.error)
  const navigate = useNavigate()

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault()
    await login(username, password)
    const me = useAuthStore.getState().user
    navigate(me ? '/' : '/login')
  }

  return (
    <div className="min-h-screen grid place-items-center bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 text-slate-100">
      <div className="w-full max-w-md rounded-2xl bg-slate-900/60 backdrop-blur border border-slate-700 p-8 shadow-xl">
        <div className="mb-6 text-center">
          <h1 className="text-2xl font-semibold">Mandari Admin</h1>
          <p className="text-slate-400">Anmeldung</p>
        </div>
        <form onSubmit={onSubmit} className="grid gap-4">
          <div>
            <label className="block text-sm mb-1">Benutzername</label>
            <input className="w-full rounded-lg bg-slate-800 border border-slate-700 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-brand-500" value={username} onChange={e => setUsername(e.target.value)} />
          </div>
          <div>
            <label className="block text-sm mb-1">Passwort</label>
            <input className="w-full rounded-lg bg-slate-800 border border-slate-700 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-brand-500" type="password" value={password} onChange={e => setPassword(e.target.value)} />
          </div>
          <div className="flex items-center justify-between mt-2">
            <button disabled={loading} type="submit" className="inline-flex justify-center items-center gap-2 rounded-lg bg-brand hover:opacity-90 disabled:opacity-60 px-4 py-2 font-medium">
              Einloggen
            </button>
            <a className="text-sm text-brand hover:opacity-90" href="/reset">Passwort vergessen?</a>
          </div>
          {error ? (<div className="text-sm text-red-400">{error}</div>) : null}
        </form>
      </div>
    </div>
  )
}


