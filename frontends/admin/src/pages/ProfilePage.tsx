import React from 'react'
import { useAuthStore } from '../stores/auth'

export function ProfilePage() {
  const user = useAuthStore(s => s.user)
  return (
    <div className="p-6 grid gap-4">
      <h1 className="text-xl font-semibold">Profil</h1>
      {!user ? (
        <p className="text-slate-400">Nicht eingeloggt.</p>
      ) : (
        <div className="grid gap-4 bg-slate-900 border border-slate-800 rounded p-4">
          <div className="grid md:grid-cols-2 gap-4">
            <div>
              <div className="text-xs text-slate-400">Benutzername</div>
              <div className="text-sm">{user.username}</div>
            </div>
            <div>
              <div className="text-xs text-slate-400">Rolle</div>
              <div className="text-sm">{user.role || '—'}</div>
            </div>
            <div>
              <div className="text-xs text-slate-400">Mandant</div>
              <div className="text-sm">{user.tenant ?? '—'}</div>
            </div>
            <div>
              <div className="text-xs text-slate-400">Status</div>
              <div className="text-sm">{user.is_superuser ? 'Superuser' : user.is_staff ? 'Admin' : 'Nutzer'}</div>
            </div>
          </div>
          <div className="text-xs text-slate-500">Demnächst: Sprache, Benachrichtigungen, MFA-Verwaltung.</div>
        </div>
      )}
    </div>
  )
}



