import { create } from 'zustand'
import { api } from '../lib/api'

export type Branding = {
  id?: number
  name?: string
  slug?: string
  logo_url: string
  color_primary: string
  color_secondary: string
}

type BrandingState = {
  branding: Branding
  loadBranding: () => Promise<void>
}

export const useBrandingStore = create<BrandingState>((set) => ({
  branding: { logo_url: '', color_primary: '#0a75ff', color_secondary: '#0f172a' },
  loadBranding: async () => {
    try {
      const b = await api('/tenants/branding/')
      const root = document.documentElement
      root.style.setProperty('--brand-primary', b.color_primary || '#0a75ff')
      root.style.setProperty('--brand-secondary', b.color_secondary || '#0f172a')
      set({ branding: b })
    } catch {
      // noop
    }
  }
}))


