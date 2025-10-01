const API_BASE = '/api'

export async function api(path: string, init?: RequestInit, xTenant?: string | number) {
  const headers: Record<string, string> = { 'Content-Type': 'application/json' }
  if (xTenant) headers['X-Tenant'] = String(xTenant)
  const res = await fetch(`${API_BASE}${path}`, {
    credentials: 'include',
    headers: { ...headers, ...(init?.headers as any) },
    ...init,
  })
  if (!res.ok) throw new Error(await res.text())
  const contentType = res.headers.get('content-type') || ''
  return contentType.includes('application/json') ? res.json() : res.text()
}


