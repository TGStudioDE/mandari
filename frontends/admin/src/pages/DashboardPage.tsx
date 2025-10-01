import React from 'react'
import { api } from '../lib/api'
import { Link } from 'react-router-dom'

type Org = { id: number; name: string; is_active: boolean }
type Log = { id: number; action: string; at: string }

export function DashboardPage() {
  const [orgs, setOrgs] = React.useState<Org[]>([])
  const [logs, setLogs] = React.useState<Log[]>([])
  const [loading, setLoading] = React.useState(true)

  React.useEffect(() => { (async () => {
    try {
      const [orgsRes, logsRes] = await Promise.all([
        api('/admin/orgs/'),
        api('/admin/audit-logs/?since=' + new Date(Date.now() - 7*24*3600*1000).toISOString()),
      ])
      setOrgs(orgsRes)
      setLogs(logsRes)
    } finally {
      setLoading(false)
    }
  })() }, [])

  const activeOrgs = orgs.filter(o => o.is_active).length

  return (
    <div className="grid gap-6">
      <h1 className="text-xl font-semibold">Admin Dashboard</h1>
      <section className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card title="Organisationen" value={orgs.length} subtitle={`${activeOrgs} aktiv`} />
        <QuickLink href="/orgs" label="Organisationen verwalten" />
        <QuickLink href="/space-roles" label="Space-Rollen verwalten" />
      </section>
      <section className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <QuickLink href="/audit-logs" label="Audit Logs ansehen" />
        <QuickLink href="/mfa-setup" label="MFA einrichten" />
        <QuickLink href="/accept-invite" label="Einladung annehmen (Test)" />
      </section>
      <section>
        <h2 className="text-lg mb-2">Letzte Aktivitäten</h2>
        <div className="bg-slate-900 border border-slate-800 rounded">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-slate-400">
                <th className="py-2 px-3">Zeit</th>
                <th className="px-3">Aktion</th>
              </tr>
            </thead>
            <tbody>
              {(logs || []).slice(0, 10).map(l => (
                <tr key={l.id} className="border-t border-slate-800">
                  <td className="py-2 px-3">{new Date(l.at).toLocaleString()}</td>
                  <td className="px-3">{l.action}</td>
                </tr>
              ))}
              {!loading && logs.length === 0 ? (
                <tr><td className="py-3 px-3 text-slate-500" colSpan={2}>Keine Aktivitäten</td></tr>
              ) : null}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  )
}

function Card({ title, value, subtitle }: { title: string; value: number | string; subtitle?: string }) {
  return (
    <div className="bg-slate-900 border border-slate-800 rounded p-4">
      <div className="text-slate-400 text-sm">{title}</div>
      <div className="text-2xl font-semibold">{value}</div>
      {subtitle ? <div className="text-slate-500 text-sm">{subtitle}</div> : null}
    </div>
  )
}

function QuickLink({ href, label }: { href: string; label: string }) {
  return (
    <Link to={href} className="bg-slate-900 border border-slate-800 rounded p-4 block hover:bg-slate-800">
      <div className="text-slate-300">{label}</div>
      <div className="text-slate-500 text-sm">Weiter</div>
    </Link>
  )
}


