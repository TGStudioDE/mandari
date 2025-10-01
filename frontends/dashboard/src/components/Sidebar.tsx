import React from 'react'
import { NavLink } from 'react-router-dom'
import { useBrandingStore } from '../stores/branding'

export function Sidebar() {
  const branding = useBrandingStore(s => s.branding)
  const linkClass = ({isActive}:{isActive:boolean}) => `px-3 py-2 rounded ${isActive ? 'bg-slate-800 text-white' : 'hover:bg-slate-800'}`
  return (
    <aside className="border-r border-slate-800 p-4 bg-slate-900/60 h-full">
      <div className="flex items-center gap-2 mb-4">
        {branding.logo_url ? (
          <img src={branding.logo_url} alt="Logo" className="h-6 w-auto" />
        ) : (
          <h2 className="text-lg font-semibold">Mandari</h2>
        )}
      </div>
      <nav className="grid gap-1">
        <NavLink to="/search" className={linkClass}>Suche</NavLink>
        <NavLink to="/agenda" className={linkClass}>Meine Agenda</NavLink>
        <NavLink to="/motions" className={linkClass}>Meine Anträge</NavLink>
        <NavLink to="/roles" className={linkClass}>Rollen & Gremien</NavLink>
      </nav>
    </aside>
  )
}


