import { create } from 'zustand'

type TenantState = {
  tenantId: number | null
  tenantHeader: string | null
  setTenantId: (id: number | null) => void
  setTenantHeader: (value: string | null) => void
}

export const useTenantStore = create<TenantState>((set) => ({
  tenantId: 1,
  tenantHeader: null,
  setTenantId: (id) => set({ tenantId: id }),
  setTenantHeader: (value) => set({ tenantHeader: value }),
}))


