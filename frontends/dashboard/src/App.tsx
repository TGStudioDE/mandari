import React from 'react'
import { Route, Routes, Navigate, useLocation } from 'react-router-dom'
import { useAuthStore } from './stores/auth'
import { LoginPage, ResetPage, BrowsePage, AgendaPage, RolesPage, SearchPage, MyMotionsPage } from './pages'
import { useBrandingStore } from './stores/branding'
import { Sidebar } from './components/Sidebar'

function RequireAuth({ children }: { children: React.ReactNode }) {
  const user = useAuthStore(s => s.user)
  if (!user) return <Navigate to="/login" replace />
  return <>{children}</>
}

export default function App() {
  const user = useAuthStore(s => s.user)
  const logout = useAuthStore(s => s.logout)
  const loc = useLocation()
  const isAuthRoute = loc.pathname.startsWith('/login') || loc.pathname.startsWith('/reset')
  const branding = useBrandingStore(s => s.branding)
  return (
    <div className={isAuthRoute ? 'min-h-screen bg-slate-950 text-slate-100' : 'min-h-screen grid grid-cols-[240px_1fr] bg-slate-950 text-slate-100'}>
      {isAuthRoute ? null : (<Sidebar />)}
      <main className={isAuthRoute ? '' : 'p-6'}>
        {!isAuthRoute && (
          <header className="flex items-center justify-between gap-3 mb-6">
            <div className="flex-1 max-w-xl">
              <form action="/search">
                <input name="q" placeholder="Suchen..." className="w-full rounded bg-slate-800 border border-slate-700 px-3 py-2" />
              </form>
            </div>
            <div className="flex items-center gap-3">
              {user ? (
                <>
                  <span className="text-sm text-slate-400">{user.username}</span>
                  <button className="px-3 py-1.5 rounded bg-slate-800 hover:bg-slate-700" onClick={logout}>Logout</button>
                </>
              ) : null}
            </div>
          </header>
        )}
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/reset" element={<ResetPage />} />
          <Route path="/browse" element={<RequireAuth><BrowsePage /></RequireAuth>} />
          <Route path="/search" element={<RequireAuth><SearchPage /></RequireAuth>} />
          <Route path="/roles" element={<RequireAuth><RolesPage /></RequireAuth>} />
          <Route path="/agenda" element={<RequireAuth><AgendaPage /></RequireAuth>} />
          <Route path="/motions" element={<RequireAuth><MyMotionsPage /></RequireAuth>} />
          <Route path="*" element={<Navigate to="/browse" replace />} />
        </Routes>
      </main>
    </div>
  )
}


