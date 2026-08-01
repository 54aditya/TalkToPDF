import React, { useState, useEffect, useRef } from 'react'
import { useParams, Link, useNavigate } from 'react-router-dom'
import { 
  Mic, 
  MicOff, 
  Send, 
  Sparkles, 
  ArrowLeft, 
  FileText, 
  ChevronDown,
  Volume2,
  Loader2,
  AlertTriangle
} from 'lucide-react'
import { useChatStore } from '../store/useChatStore'
import { api } from '../services/api'

export default function Chat() {
  const { chatId } = useParams()
  const navigate = useNavigate()

  
  const {
    activeSession,
    messages,
    sending,
    loadSession,
    addMessage,
    appendToLastAssistantMessage,
    setLastAssistantCitations,
    setSending,
  } = useChatStore()

  const [inputText, setInputText] = useState('')
  const [isRecording, setIsRecording] = useState(false)
  const [activeCitation, setActiveCitation] = useState(null)
  const [sessionError, setSessionError] = useState(null)
  const [docContext, setDocContext] = useState(null)

  const messageEndRef = useRef(null)
  const mediaRecorderRef = useRef(null)
  const audioChunksRef = useRef([])

  
  useEffect(() => {
    if (!chatId) return
    loadSession(chatId).catch((err) => {
      setSessionError(err.message)
    })
  }, [chatId])

  
  useEffect(() => {
    if (!activeSession?.document_ids?.length) return
    const firstDocId = activeSession.document_ids[0]
    api.getDocumentContext(firstDocId)
      .then(setDocContext)
      .catch(() => {})
  }, [activeSession])

  
  useEffect(() => {
    messageEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  
  const handleSend = async (queryText) => {
    const text = (queryText || inputText).trim()
    if (!text || sending) return
    setInputText('')
    setSessionError(null)

    
    addMessage({ id: Date.now() + '-u', role: 'user', content: text, citations: [] })
    
    addMessage({ id: Date.now() + '-a', role: 'assistant', content: '', citations: [] })

    setSending(true)
    try {
      await api.streamChatQuery({
        documentIds: activeSession?.document_ids || [],
        query: text,
        onCitations: (citations) => {
          setLastAssistantCitations(citations)
        },
        onToken: (token) => {
          appendToLastAssistantMessage(token)
        },
        onDone: async () => {
          setSending(false)
          
          if (activeSession?._id) {
            await api.addSessionMessage(activeSession._id, 'user', text).catch(() => {})
            const lastMsg = useChatStore.getState().messages.slice(-1)[0]
            await api.addSessionMessage(
              activeSession._id,
              'assistant',
              lastMsg?.content || '',
              lastMsg?.citations || []
            ).catch(() => {})
          }
        },
        onError: (errMsg) => {
          appendToLastAssistantMessage(errMsg)
          setSending(false)
        },
      })
    } catch (err) {
      setSessionError(err.message)
      setSending(false)
    }

    
    
    synthesizeAndPlay()
  }

  
  const synthesizeAndPlay = async () => {
    
    await new Promise((r) => setTimeout(r, 500))
    const last = useChatStore.getState().messages.slice(-1)[0]
    if (!last || last.role !== 'assistant' || !last.content) return
    try {
      const blob = await api.synthesizeSpeech(last.content.slice(0, 1200))
      const url = URL.createObjectURL(blob)
      const audio = new Audio(url)
      audio.play().catch(() => {}) 
    } catch {
      
    }
  }

  
  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      audioChunksRef.current = []
      
      let options = {}
      if (typeof MediaRecorder.isTypeSupported === 'function') {
        if (MediaRecorder.isTypeSupported('audio/webm')) {
          options = { mimeType: 'audio/webm' }
        } else if (MediaRecorder.isTypeSupported('audio/mp4')) {
          options = { mimeType: 'audio/mp4' }
        } else if (MediaRecorder.isTypeSupported('audio/ogg')) {
          options = { mimeType: 'audio/ogg' }
        } else if (MediaRecorder.isTypeSupported('audio/wav')) {
          options = { mimeType: 'audio/wav' }
        }
      }

      const recorder = new MediaRecorder(stream, options)
      recorder.ondataavailable = (e) => {
        if (e.data.size > 0) audioChunksRef.current.push(e.data)
      }
      recorder.onstop = async () => {
        stream.getTracks().forEach((t) => t.stop())
        const blob = new Blob(audioChunksRef.current, { type: recorder.mimeType || 'audio/webm' })
        try {
          const transcript = await api.transcribeAudio(blob)
          if (transcript) {
            await handleSend(transcript)
          }
        } catch (err) {
          setSessionError(`Voice transcription failed: ${err.message}`)
        }
      }
      mediaRecorderRef.current = recorder
      recorder.start()
      setIsRecording(true)
    } catch (err) {
      setSessionError('Microphone access denied. Please allow microphone permissions.')
    }
  }

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop()
      setIsRecording(false)
    }
  }

  const toggleRecording = () => {
    if (isRecording) stopRecording()
    else startRecording()
  }

  const handleFormSubmit = (e) => {
    e.preventDefault()
    handleSend()
  }

  
  if (sessionError && messages.length === 0) {
    return (
      <div className="h-[calc(100vh-4rem)] flex items-center justify-center p-8">
        <div className="flex flex-col items-center gap-4 text-center max-w-sm">
          <AlertTriangle className="h-10 w-10 text-rose-400" />
          <p className="text-sm text-slate-300 font-semibold">Failed to load session</p>
          <p className="text-xs text-slate-500">{sessionError}</p>
          <button
            onClick={() => navigate('/dashboard')}
            className="px-4 py-2 bg-brand-600 text-white rounded-xl text-xs font-semibold hover:bg-brand-500 transition-colors"
          >
            Back to Library
          </button>
        </div>
      </div>
    )
  }

  const docNames = docContext?.filename || activeSession?.document_ids?.join(', ') || 'Loading...'

  return (
    <div className="h-[calc(100vh-4rem)] flex flex-col bg-slate-950">
      
      <div className="h-14 px-6 border-b border-slate-900 flex items-center gap-4 bg-slate-900/40">
        <Link to="/dashboard" className="p-1.5 hover:bg-slate-800 text-slate-400 hover:text-white rounded-lg transition-colors">
          <ArrowLeft className="h-4 w-4" />
        </Link>
        <div className="flex-1 min-w-0">
          <h2 className="text-sm font-semibold truncate">
            {activeSession?.title || 'Research Chat'}
          </h2>
          <p className="text-[10px] text-slate-500 truncate flex items-center gap-1.5">
            <FileText className="h-3 w-3 text-brand-400 shrink-0" />
            <span>{docNames}</span>
            {docContext?.page_count && (
              <span className="text-slate-600">· {docContext.page_count} pages</span>
            )}
          </p>
        </div>
        {sending && (
          <div className="flex items-center gap-1.5 text-[10px] text-brand-400">
            <Loader2 className="h-3.5 w-3.5 animate-spin" />
            <span>Thinking...</span>
          </div>
        )}
      </div>

      
      {sessionError && (
        <div className="px-6 py-2 bg-rose-500/10 border-b border-rose-500/20 text-rose-400 text-[11px] flex items-center gap-2">
          <AlertTriangle className="h-3.5 w-3.5 shrink-0" />
          <span>{sessionError}</span>
        </div>
      )}

      
      {docContext?.summary && messages.length === 0 && (
        <div className="px-6 py-3 bg-brand-500/5 border-b border-brand-500/10">
          <p className="text-[11px] text-slate-400 leading-relaxed">
            <span className="font-semibold text-brand-400">Summary: </span>
            {docContext.summary}
          </p>
        </div>
      )}

      
      <div className="flex-1 overflow-y-auto px-6 py-6 space-y-6">
        {messages.length === 0 && !sending && (
          <div className="flex flex-col items-center justify-center h-full gap-4 text-center">
            <div className="p-4 bg-brand-500/10 border border-brand-500/20 rounded-2xl">
              <Sparkles className="h-8 w-8 text-brand-400" />
            </div>
            <p className="text-sm font-semibold text-slate-300">Ask a research question</p>
            <p className="text-xs text-slate-500 max-w-xs">
              Type a question or click the microphone to speak. I'll answer using the content of your uploaded papers.
            </p>
          </div>
        )}

        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`flex gap-4 max-w-3xl ${msg.role === 'user' ? 'ml-auto flex-row-reverse' : ''}`}
          >
            {/* Avatar */}
            <div className={`h-8 w-8 rounded-lg shrink-0 flex items-center justify-center font-bold text-xs
              ${msg.role === 'user'
                ? 'bg-slate-800 text-slate-200'
                : 'bg-brand-500/10 text-brand-400 border border-brand-500/20'}`}
            >
              {msg.role === 'user' ? 'U' : <Sparkles className="h-3.5 w-3.5" />}
            </div>

            {/* Bubble */}
            <div className="space-y-3 min-w-0">
              <div className={`px-4 py-3 rounded-2xl text-xs leading-relaxed break-words shadow-sm
                ${msg.role === 'user'
                  ? 'bg-brand-600 text-white rounded-tr-none'
                  : 'bg-slate-900/70 border border-slate-800/80 rounded-tl-none text-slate-200'}`}
              >
                {msg.content || (
                  msg.role === 'assistant' && sending && (
                    <span className="flex items-center gap-1.5 text-slate-500">
                      <Loader2 className="h-3 w-3 animate-spin" />
                      <span>Generating response...</span>
                    </span>
                  )
                )}
              </div>

              {/* Citations */}
              {msg.citations?.length > 0 && (
                <div className="flex flex-wrap gap-2">
                  {msg.citations.map((cite, i) => (
                    <button
                      key={i}
                      onClick={() => setActiveCitation(activeCitation === cite ? null : cite)}
                      className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-[10px] font-semibold bg-slate-900 border border-slate-800 hover:border-brand-500 text-slate-400 hover:text-brand-300 transition-all cursor-pointer"
                    >
                      <FileText className="h-3 w-3 text-brand-400" />
                      <span>{cite.filename} (pg. {cite.page})</span>
                      <ChevronDown className={`h-3 w-3 transition-transform ${activeCitation === cite ? 'rotate-180' : ''}`} />
                    </button>
                  ))}
                </div>
              )}

              {/* Expanded citation */}
              {activeCitation && msg.citations?.includes(activeCitation) && (
                <div className="p-3 bg-slate-900/40 border border-slate-800 rounded-xl space-y-2 max-w-md">
                  <div className="flex justify-between items-center text-[10px] text-slate-400 border-b border-slate-800/50 pb-1.5">
                    <span className="font-semibold">{activeCitation.filename} — Page {activeCitation.page}</span>
                    <span className="text-brand-400 font-bold uppercase tracking-wider text-[8px] border border-brand-500/20 px-1.5 py-0.5 rounded bg-brand-500/5">
                      Verbatim
                    </span>
                  </div>
                  <p className="text-[10px] text-slate-300 leading-relaxed italic">
                    "{activeCitation.snippet}"
                  </p>
                </div>
              )}
            </div>
          </div>
        ))}
        <div ref={messageEndRef} />
      </div>

      {/* Voice recording indicator */}
      {isRecording && (
        <div className="h-16 flex items-center justify-center gap-3 border-t border-slate-900/60 bg-slate-900/20 px-6">
          <div className="flex items-center gap-2 text-xs font-semibold text-brand-400 animate-pulse">
            <Volume2 className="h-4 w-4" />
            <span>Listening... Click mic to stop</span>
          </div>
          <div className="flex items-end gap-0.5 h-6">
            <span className="w-1 bg-brand-500 rounded-full animate-[bounce_0.8s_infinite] h-3" />
            <span className="w-1 bg-brand-400 rounded-full animate-[bounce_0.5s_infinite] h-5" />
            <span className="w-1 bg-brand-500 rounded-full animate-[bounce_0.7s_infinite] h-2" />
            <span className="w-1 bg-brand-400 rounded-full animate-[bounce_0.6s_infinite] h-4" />
            <span className="w-1 bg-brand-500 rounded-full animate-[bounce_0.9s_infinite] h-3" />
          </div>
        </div>
      )}

      {/* Input panel */}
      <div className="p-4 border-t border-slate-900/80 bg-slate-900/40">
        <form onSubmit={handleFormSubmit} className="flex gap-3 max-w-3xl mx-auto">
          {/* Mic button */}
          <button
            type="button"
            onClick={toggleRecording}
            disabled={sending}
            className={`p-3 rounded-xl flex items-center justify-center cursor-pointer transition-all border disabled:opacity-40
              ${isRecording
                ? 'bg-rose-500 border-rose-600 text-white animate-pulse'
                : 'bg-slate-900 border-slate-800 text-slate-400 hover:text-white hover:border-slate-700'}`}
            title={isRecording ? 'Stop recording' : 'Start voice input'}
          >
            {isRecording ? <MicOff className="h-5 w-5" /> : <Mic className="h-5 w-5" />}
          </button>

          {/* Text input */}
          <input
            type="text"
            placeholder={isRecording ? 'Listening...' : 'Ask a research question...'}
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            disabled={isRecording || sending}
            className="flex-1 bg-slate-900 border border-slate-800 text-xs rounded-xl px-4 focus:outline-none focus:border-brand-500 disabled:opacity-40 text-slate-100 placeholder-slate-500 transition-colors"
          />

          {/* Send button */}
          <button
            type="submit"
            disabled={!inputText.trim() || isRecording || sending}
            className="p-3 bg-brand-600 disabled:opacity-45 hover:bg-brand-500 text-white rounded-xl flex items-center justify-center cursor-pointer transition-colors shadow-lg shadow-brand-600/25"
          >
            {sending ? <Loader2 className="h-4 w-4 animate-spin" /> : <Send className="h-4 w-4" />}
          </button>
        </form>
      </div>
    </div>
  )
}
