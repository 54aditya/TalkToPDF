

const API_BASE_URL = '/api/v1'


function getToken() {
  try {
    const raw = localStorage.getItem('auth-storage')
    if (!raw) return null
    return JSON.parse(raw)?.state?.token || null
  } catch {
    return null
  }
}


function buildHeaders(extra = {}) {
  const headers = { 'Content-Type': 'application/json', ...extra }
  const token = getToken()
  if (token) headers['Authorization'] = `Bearer ${token}`
  return headers
}


async function request(url, options = {}) {
  const response = await fetch(url, {
    ...options,
    headers: buildHeaders(options.headers),
  })
  if (!response.ok) {
    const err = await response.json().catch(() => ({}))
    throw new Error(err.detail || err.message || `Request failed (${response.status})`)
  }
  return response.json()
}

export const api = {
  

  async listDocuments() {
    return request(`${API_BASE_URL}/documents`)
  },

  async getDocument(id) {
    return request(`${API_BASE_URL}/documents/${id}`)
  },

  async deleteDocument(id) {
    return request(`${API_BASE_URL}/documents/${id}`, { method: 'DELETE' })
  },

  
  uploadDocument(file, onProgress) {
    return new Promise((resolve, reject) => {
      const xhr = new XMLHttpRequest()
      xhr.open('POST', `${API_BASE_URL}/documents/upload`)

      const token = getToken()
      if (token) xhr.setRequestHeader('Authorization', `Bearer ${token}`)

      if (xhr.upload && onProgress) {
        xhr.upload.addEventListener('progress', (event) => {
          if (event.lengthComputable) {
            onProgress(Math.round((event.loaded * 100) / event.total))
          }
        })
      }

      xhr.onload = () => {
        if (xhr.status >= 200 && xhr.status < 300) {
          try { resolve(JSON.parse(xhr.responseText)) }
          catch { reject(new Error('Invalid response from server.')) }
        } else {
          try {
            const err = JSON.parse(xhr.responseText)
            reject(new Error(err.detail || err.message || 'Upload failed.'))
          } catch {
            reject(new Error(`Upload failed with status ${xhr.status}`))
          }
        }
      }
      xhr.onerror = () => reject(new Error('Network error occurred.'))

      const form = new FormData()
      form.append('file', file)
      xhr.send(form)
    })
  },

  

  async register(name, email, password) {
    const res = await fetch(`${API_BASE_URL}/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, email, password }),
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || err.message || 'Registration failed.')
    }
    return res.json()
  },

  async login(email, password) {
    const res = await fetch(`${API_BASE_URL}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || err.message || 'Invalid email or password.')
    }
    return res.json()
  },

  async getMe(token) {
    const res = await fetch(`${API_BASE_URL}/auth/me`, {
      headers: { Authorization: `Bearer ${token}` },
    })
    if (!res.ok) throw new Error('Failed to fetch user profile.')
    return res.json()
  },

  

  
  async streamChatQuery({ documentIds, query, onCitations, onToken, onDone, onError }) {
    const token = getToken()
    const headers = { 'Content-Type': 'application/json' }
    if (token) headers['Authorization'] = `Bearer ${token}`

    const response = await fetch(`${API_BASE_URL}/chat/query`, {
      method: 'POST',
      headers,
      body: JSON.stringify({ document_ids: documentIds, query, top_k: 5 }),
    })

    if (!response.ok) {
      const err = await response.json().catch(() => ({}))
      throw new Error(err.detail || err.message || 'Chat query failed.')
    }

    const reader = response.body.getReader()
    const decoder = new TextDecoder()
    let buffer = ''

    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split('\n')
      buffer = lines.pop() 

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          try {
            const event = JSON.parse(line.slice(6))
            if (event.type === 'citations') onCitations?.(event.data)
            else if (event.type === 'token') onToken?.(event.content)
            else if (event.type === 'done') onDone?.()
            else if (event.type === 'error') onError?.(event.content)
          } catch {
            
          }
        }
      }
    }
  },

  async getDocumentContext(documentId) {
    return request(`${API_BASE_URL}/chat/context/${documentId}`)
  },

  

  
  async transcribeAudio(audioBlob) {
    const token = getToken()
    const formData = new FormData()
    
    let filename = 'recording.webm'
    if (audioBlob.type) {
      if (audioBlob.type.includes('wav')) filename = 'recording.wav'
      else if (audioBlob.type.includes('mp4')) filename = 'recording.mp4'
      else if (audioBlob.type.includes('mpeg')) filename = 'recording.mp3'
      else if (audioBlob.type.includes('ogg')) filename = 'recording.ogg'
    }
    
    formData.append('audio', audioBlob, filename)

    const headers = {}
    if (token) headers['Authorization'] = `Bearer ${token}`

    const res = await fetch(`${API_BASE_URL}/voice/transcribe`, {
      method: 'POST',
      headers,
      body: formData,
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || err.message || 'Transcription failed.')
    }
    const data = await res.json()
    return data.transcript
  },

  
  async synthesizeSpeech(text) {
    const token = getToken()
    const headers = { 'Content-Type': 'application/json' }
    if (token) headers['Authorization'] = `Bearer ${token}`

    const res = await fetch(`${API_BASE_URL}/voice/synthesize`, {
      method: 'POST',
      headers,
      body: JSON.stringify({ text }),
    })
    if (!res.ok) throw new Error('Speech synthesis failed.')
    return res.blob()
  },

  

  async listSessions() {
    return request(`${API_BASE_URL}/sessions`)
  },

  async createSession(documentIds, title) {
    return request(`${API_BASE_URL}/sessions`, {
      method: 'POST',
      body: JSON.stringify({ document_ids: documentIds, title }),
    })
  },

  async getSession(sessionId) {
    return request(`${API_BASE_URL}/sessions/${sessionId}`)
  },

  async deleteSession(sessionId) {
    return request(`${API_BASE_URL}/sessions/${sessionId}`, { method: 'DELETE' })
  },

  async addSessionMessage(sessionId, role, content, citations = []) {
    return request(`${API_BASE_URL}/sessions/${sessionId}/messages`, {
      method: 'POST',
      body: JSON.stringify({ role, content, citations }),
    })
  },
}
