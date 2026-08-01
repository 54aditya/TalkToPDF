import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { api } from '../services/api'

export const useAuthStore = create(
  persist(
    (set, get) => ({
      user: null,
      token: null,
      loading: false,
      error: null,

      
      login: async (email, password) => {
        set({ loading: true, error: null })
        try {
          const { access_token } = await api.login(email, password)
          
          const user = await api.getMe(access_token)
          set({ token: access_token, user, loading: false })
        } catch (err) {
          set({ error: err.message, loading: false })
          throw err
        }
      },

      
      register: async (name, email, password) => {
        set({ loading: true, error: null })
        try {
          const { access_token } = await api.register(name, email, password)
          const user = await api.getMe(access_token)
          set({ token: access_token, user, loading: false })
        } catch (err) {
          set({ error: err.message, loading: false })
          throw err
        }
      },

      
      logout: () => {
        set({ user: null, token: null, error: null })
      },

      isAuthenticated: () => !!get().token,
    }),
    {
      name: 'auth-storage',
      
      partialize: (state) => ({ token: state.token, user: state.user }),
    }
  )
)
