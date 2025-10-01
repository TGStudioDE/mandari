import React from 'react'
import { api } from '../lib/api'

export function MfaSetupPage() {
  const [secret, setSecret] = React.useState('')
  const [otpauthUrl, setOtpauthUrl] = React.useState('')
  const [recovery, setRecovery] = React.useState<string[]>([])
  const [otp, setOtp] = React.useState('')
  const [status, setStatus] = React.useState('')

  async function setup() {
    const res = await api('/auth/mfa/setup/', { method: 'POST' })
    setSecret(res.secret)
    setOtpauthUrl(res.otpauth_url)
    setRecovery(res.recovery_codes)
  }

  async function enable(e: React.FormEvent) {
    e.preventDefault()
    setStatus('')
    try {
      await api('/auth/mfa/enable/', { method: 'POST', body: JSON.stringify({ otp }) })
      setStatus('MFA aktiviert.')
    } catch (e: any) {
      setStatus(e?.message || 'Fehler')
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-950 text-slate-100 p-6">
      <div className="w-full max-w-lg bg-slate-900 border border-slate-800 p-6 rounded grid gap-4">
        <h1 className="text-lg font-semibold">MFA Setup</h1>
        <button className="px-3 py-2 rounded bg-slate-800" onClick={setup}>Secret erzeugen</button>
        {secret ? (
          <div className="grid gap-2">
            <div className="text-sm">Secret: <span className="font-mono">{secret}</span></div>
            {otpauthUrl ? (
              <div className="text-sm break-all">otpauth: {otpauthUrl}</div>
            ) : null}
            <div>
              <div className="text-sm mb-1">Recovery-Codes:</div>
              <ul className="text-sm grid gap-1">
                {recovery.map((r, i) => <li key={i} className="font-mono">{r}</li>)}
              </ul>
            </div>
            <form onSubmit={enable} className="grid gap-2">
              <input className="px-3 py-2 rounded bg-slate-800 border border-slate-700" placeholder="TOTP-Code" value={otp} onChange={e => setOtp(e.target.value)} />
              <button className="px-3 py-2 rounded bg-blue-600 hover:bg-blue-500" type="submit">MFA aktivieren</button>
            </form>
            {status ? <div className="text-sm text-slate-300">{status}</div> : null}
          </div>
        ) : null}
      </div>
    </div>
  )
}


