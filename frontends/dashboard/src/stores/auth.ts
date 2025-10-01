import { create } from 'zustand'
import { api } from '../lib/api'

export type User = {
  id: number
  username: string
  tenant: number | null
  role: string | null
  is_staff: boolean
  is_superuser: boolean
}

type AuthState = {
  user: User | null
  loading: boolean
  error: string | null
  login: (username: string, password: string) => Promise<void>
  fetchMe: () => Promise<void>
  logout: () => Promise<void>
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  loading: false,
  error: null,
  login: async (username, password) => {
    set({ loading: true, error: null })
    await api('/auth/login/', { method: 'POST', body: JSON.stringify({ username, password }) })
    await useAuthStore.getState().fetchMe()
    set({ loading: false })
  },
  fetchMe: async () => {
    try {
      const me = await api('/auth/me/')
      set({ user: me })
    } catch (e) {
      set({ user: null })
    }
  },
  logout: async () => {
    await api('/auth/logout/', { method: 'POST' })
    set({ user: null })
  }
}))


