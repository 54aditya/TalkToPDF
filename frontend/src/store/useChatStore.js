import { create } from 'zustand'
import { api } from '../services/api'

export const useChatStore = create((set, get) => ({
  sessions: [],
  activeSession: null,
  messages: [],
  loadingSessions: false,
  sending: false,
  error: null,

  
  fetchSessions: async () => {
    set({ loadingSessions: true, error: null })
    try {
      const sessions = await api.listSessions()
      set({ sessions, loadingSessions: false })
    } catch (err) {
      set({ error: err.message, loadingSessions: false })
    }
  },

  
  createSession: async (documentIds, title) => {
    try {
      const session = await api.createSession(documentIds, title)
      set((state) => ({
        sessions: [session, ...state.sessions],
        activeSession: session,
        messages: [],
      }))
      return session
    } catch (err) {
      set({ error: err.message })
      throw err
    }
  },

  
  loadSession: async (sessionId) => {
    try {
      const session = await api.getSession(sessionId)
      set({
        activeSession: session,
        messages: session.messages || [],
        error: null,
      })
      return session
    } catch (err) {
      set({ error: err.message })
      throw err
    }
  },

  
  deleteSession: async (sessionId) => {
    try {
      await api.deleteSession(sessionId)
      set((state) => ({
        sessions: state.sessions.filter((s) => s._id !== sessionId),
        activeSession: state.activeSession?._id === sessionId ? null : state.activeSession,
        messages: state.activeSession?._id === sessionId ? [] : state.messages,
      }))
    } catch (err) {
      set({ error: err.message })
      throw err
    }
  },

  
  addMessage: (message) => {
    set((state) => ({ messages: [...state.messages, message] }))
  },

  
  appendToLastAssistantMessage: (token) => {
    set((state) => {
      const msgs = [...state.messages]
      const last = msgs[msgs.length - 1]
      if (last && last.role === 'assistant') {
        msgs[msgs.length - 1] = { ...last, content: last.content + token }
      }
      return { messages: msgs }
    })
  },

  
  setLastAssistantCitations: (citations) => {
    set((state) => {
      const msgs = [...state.messages]
      const last = msgs[msgs.length - 1]
      if (last && last.role === 'assistant') {
        msgs[msgs.length - 1] = { ...last, citations }
      }
      return { messages: msgs }
    })
  },

  setSending: (val) => set({ sending: val }),
  clearError: () => set({ error: null }),
}))
