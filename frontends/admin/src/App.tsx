import React from 'react'
import { Route, Routes, Navigate, Link, useLocation } from 'react-router-dom'
import { useAuthStore } from './stores/auth'
import { LoginPage } from './pages/LoginPage'
import { ResetPage } from './pages/ResetPage'
import { TenantsPage } from './pages/TenantsPage'
import { OParlPage } from './pages/OParlPage'
import { OrgsPage } from './pages/OrgsPage'
import { AcceptInvitePage } from './pages/AcceptInvitePage'
import { MfaSetupPage } from './pages/MfaSetupPage'
import { SpaceRolesPage } from './pages/SpaceRolesPage'
import { AuditLogsPage } from './pages/AuditLogsPage'
import { DashboardPage } from './pages/DashboardPage'
import { PlansPage } from './pages/PlansPage'
import { SettingsPage } from './pages/SettingsPage'
import { StaffPage } from './pages/StaffPage'
import { CrmPage } from './pages/CrmPage'
import { ProfilePage } from './pages/ProfilePage'
import { OrgDetailPage } from './pages/OrgDetailPage'

function RequireAuth({ children }: { children: React.ReactNode }) {
  const user = useAuthStore(s => s.user)
  if (!user) return <Navigate to="/login" replace />
  if (!user.is_superuser && !user.is_staff) return <Navigate to="/login" replace />
  return <>{children}</>
}

export default function App() {
  const user = useAuthStore(s => s.user)
  const logout = useAuthStore(s => s.logout)
  const loc = useLocation()
  const isAuthRoute = loc.pathname.startsWith('/login') || loc.pathname.startsWith('/reset') || loc.pathname.startsWith('/accept-invite')
  return (
    <div className={isAuthRoute ? 'min-h-screen bg-slate-950 text-slate-100' : 'min-h-screen grid grid-cols-[240px_1fr] bg-slate-950 text-slate-100'}>
      {isAuthRoute ? null : (
        <aside className="border-r border-slate-800 p-4 bg-slate-900/60">
          <h2 className="text-lg font-semibold mb-4">Mandari Verwaltung</h2>
          <nav className="grid gap-2">
            <span className="text-xs uppercase text-slate-500 px-3">Übersicht</span>
            <Link to="/" className="px-3 py-2 rounded hover:bg-slate-800">Dashboard</Link>
            <Link to="/crm" className="px-3 py-2 rounded hover:bg-slate-800">CRM</Link>
            <span className="text-xs uppercase text-slate-500 mt-3 px-3">Kunden</span>
            <Link to="/orgs" className="px-3 py-2 rounded hover:bg-slate-800">Organisationen</Link>
            <Link to="/space-roles" className="px-3 py-2 rounded hover:bg-slate-800">Space-Rollen</Link>
            <span className="text-xs uppercase text-slate-500 mt-3 px-3">Produkte & Anbindung</span>
            <Link to="/plans" className="px-3 py-2 rounded hover:bg-slate-800">Produkte & Preise</Link>
            <Link to="/settings" className="px-3 py-2 rounded hover:bg-slate-800">Anbindungen</Link>
            <Link to="/audit-logs" className="px-3 py-2 rounded hover:bg-slate-800">Änderungsprotokoll</Link>
            <Link to="/oparl" className="px-3 py-2 rounded hover:bg-slate-800">OParl</Link>
            <span className="text-xs uppercase text-slate-500 mt-3 px-3">Team</span>
            <Link to="/staff" className="px-3 py-2 rounded hover:bg-slate-800">Team & Berechtigungen</Link>
            <span className="text-xs uppercase text-slate-500 mt-3 px-3">Alt</span>
            <Link to="/tenants" className="px-3 py-2 rounded hover:bg-slate-800">Mandanten (Legacy)</Link>
          </nav>
        </aside>
      )}
      <main className={isAuthRoute ? '' : 'p-6'}>
        {!isAuthRoute && (
          <header className="flex justify-end gap-3 mb-6 relative">
            {user ? (
              <ProfileMenu username={user.username} onLogout={logout} />
            ) : null}
          </header>
        )}
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/reset" element={<ResetPage />} />
          <Route path="/tenants" element={<RequireAuth><TenantsPage /></RequireAuth>} />
          <Route path="/orgs" element={<RequireAuth><OrgsPage /></RequireAuth>} />
          <Route path="/oparl" element={<RequireAuth><OParlPage /></RequireAuth>} />
          <Route path="/accept-invite" element={<AcceptInvitePage />} />
          <Route path="/mfa-setup" element={<RequireAuth><MfaSetupPage /></RequireAuth>} />
          <Route path="/space-roles" element={<RequireAuth><SpaceRolesPage /></RequireAuth>} />
          <Route path="/audit-logs" element={<RequireAuth><AuditLogsPage /></RequireAuth>} />
          <Route path="/plans" element={<RequireAuth><PlansPage /></RequireAuth>} />
          <Route path="/settings" element={<RequireAuth><SettingsPage /></RequireAuth>} />
          <Route path="/staff" element={<RequireAuth><StaffPage /></RequireAuth>} />
          <Route path="/crm" element={<RequireAuth><CrmPage /></RequireAuth>} />
          <Route path="/org" element={<RequireAuth><OrgDetailPage /></RequireAuth>} />
          <Route path="/profile" element={<RequireAuth><ProfilePage /></RequireAuth>} />
          <Route path="/" element={<RequireAuth><DashboardPage /></RequireAuth>} />
          <Route path="*" element={<Navigate to={user ? '/' : '/login'} replace />} />
        </Routes>
      </main>
    </div>
  )
}


function ProfileMenu({ username, onLogout }: { username: string; onLogout: () => Promise<void> }) {
  const [open, setOpen] = React.useState(false)
  return (
    <div className="relative">
      <button className="px-3 py-1.5 rounded bg-slate-800 hover:bg-slate-700 inline-flex items-center gap-2" onClick={() => setOpen(v => !v)}>
        <span className="inline-flex items-center justify-center w-6 h-6 rounded-full bg-blue-600 text-white text-xs uppercase">
          {username.slice(0, 2)}
        </span>
        <span className="text-sm text-slate-200">{username}</span>
      </button>
      {open ? (
        <div className="absolute right-0 mt-2 w-56 rounded border border-slate-800 bg-slate-900 shadow-lg p-2 z-10">
          <div className="px-2 py-1 text-xs text-slate-500">Mein Konto</div>
          <Link to="/profile" className="block px-2 py-1 rounded hover:bg-slate-800">Profil</Link>
          <button className="w-full text-left px-2 py-1 rounded hover:bg-slate-800" onClick={onLogout}>Abmelden</button>
        </div>
      ) : null}
    </div>
  )
}


