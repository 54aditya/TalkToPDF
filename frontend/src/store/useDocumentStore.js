import { create } from 'zustand'
import { api } from '../services/api'

export const useDocumentStore = create((set, get) => ({
  documents: [],
  loading: false,
  error: null,
  uploading: false,
  uploadProgress: 0,

  fetchDocuments: async () => {
    set({ loading: true, error: null })
    try {
      const docs = await api.listDocuments()
      set({ documents: docs, loading: false })
    } catch (err) {
      set({ error: err.message, loading: false })
    }
  },

  uploadDocument: async (file) => {
    set({ uploading: true, uploadProgress: 0, error: null })
    try {
      await api.uploadDocument(file, (progress) => {
        set({ uploadProgress: progress })
      })
      
      await get().fetchDocuments()
      set({ uploading: false, uploadProgress: 0 })
    } catch (err) {
      set({ error: err.message, uploading: false, uploadProgress: 0 })
      throw err;
    }
  },

  deleteDocument: async (id) => {
    set({ error: null })
    try {
      await api.deleteDocument(id)
      set((state) => ({
        documents: state.documents.filter((doc) => doc._id !== id)
      }))
    } catch (err) {
      set({ error: err.message })
      throw err;
    }
  }
}))
