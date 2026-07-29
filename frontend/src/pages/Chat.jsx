import React, { useState, useEffect, useRef } from 'react'
import { useParams, Link } from 'react-router-dom'
import { 
  Mic, 
  MicOff, 
  Send, 
  Sparkles, 
  ArrowLeft, 
  FileText, 
  ExternalLink,
  ChevronDown,
  Volume2
} from 'lucide-react'

export default function Chat() {
  const { chatId } = useParams()
  const [messages, setMessages] = useState([
    {
      id: '1',
      role: 'assistant',
      content: 'Hello! I have analyzed **Attention Is All You Need** and **Deep Residual Learning for Image Recognition**. You can ask questions using text or click the microphone to speak.',
      citations: []
    }
  ])
  const [inputText, setInputText] = useState('')
  const [isRecording, setIsRecording] = useState(false)
  const [isSynthesizing, setIsSynthesizing] = useState(false)
  const [activeCitations, setActiveCitations] = useState(null)
  const messageEndRef = useRef(null)

  useEffect(() => {
    messageEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const handleSendText = (e) => {
    e.preventDefault()
    if (!inputText.trim()) return

    const userMessage = {
      id: String(messages.length + 1),
      role: 'user',
      content: inputText,
      citations: []
    }

    setMessages((prev) => [...prev, userMessage])
    setInputText('')

    // Simulate LLM streaming response
    simulateBotResponse(inputText)
  }

  const simulateBotResponse = (query) => {
    const responseText = "According to Section 3.1 of the Attention Is All You Need paper, the Transformer structure relies entirely on self-attention mechanisms to compute representations of its input and output without using sequence-aligned RNNs or convolution. Specifically, Scaled Dot-Product Attention maps a query and a set of key-value pairs to an output."
    
    const botMessageId = String(messages.length + 2)
    const newBotMessage = {
      id: botMessageId,
      role: 'assistant',
      content: '',
      citations: [
        {
          filename: 'Attention_Is_All_You_Need.pdf',
          page: 3,
          snippet: 'Scaled Dot-Product Attention: The input consists of queries and keys of dimension dk, and values of dimension dv. We compute the dot products of the query with all keys, divide each by sqrt(dk), and apply a softmax function.'
        }
      ]
    }

    setMessages((prev) => [...prev, newBotMessage])

    let index = 0
    const interval = setInterval(() => {
      setMessages((prev) => {
        return prev.map((msg) => {
          if (msg.id === botMessageId) {
            return {
              ...msg,
              content: responseText.slice(0, index + 3)
            }
          }
          return msg
        })
      })
      index += 3
      if (index >= responseText.length) {
        clearInterval(interval)
      }
    }, 30)
  }

  const toggleRecording = () => {
    if (isRecording) {
      setIsRecording(false)
      // Simulate STT -> LLM response
      setTimeout(() => {
        simulateBotResponse("Summarize Section 3.2")
      }, 1000)
    } else {
      setIsRecording(true)
    }
  }

  return (
    <div className="h-[calc(100vh-4rem)] flex flex-col bg-slate-950">
      {/* Header bar */}
      <div className="h-14 px-6 border-b border-slate-900 flex items-center gap-4 bg-slate-900/40">
        <Link to="/dashboard" className="p-1.5 hover:bg-slate-800 text-slate-400 hover:text-white rounded-lg transition-colors">
          <ArrowLeft className="h-4 w-4" />
        </Link>
        <div className="flex-1 min-w-0">
          <h2 className="text-sm font-semibold truncate">Active Discussion #{chatId}</h2>
          <p className="text-[10px] text-slate-500 truncate flex items-center gap-1.5">
            <FileText className="h-3 w-3 text-brand-400" />
            <span>Attention_Is_All_You_Need.pdf, ResNet_Deep_Residual_Learning.pdf</span>
          </p>
        </div>
      </div>

      {/* Message stream panel */}
      <div className="flex-1 overflow-y-auto px-6 py-6 space-y-6">
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
              {msg.role === 'user' ? 'U' : 'AI'}
            </div>

            {/* Bubble */}
            <div className="space-y-3 min-w-0">
              <div className={`px-4 py-3 rounded-2xl text-xs leading-relaxed break-words shadow-sm
                ${msg.role === 'user' 
                  ? 'bg-brand-600 text-white rounded-tr-none' 
                  : 'bg-slate-900/70 border border-slate-800/80 rounded-tl-none text-slate-200'}`}
              >
                {msg.content}
              </div>

              {/* Citations List inside Bubble */}
              {msg.citations.length > 0 && (
                <div className="flex flex-wrap gap-2">
                  {msg.citations.map((cite, i) => (
                    <button
                      key={i}
                      onClick={() => setActiveCitations(activeCitations === cite ? null : cite)}
                      className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-[10px] font-semibold bg-slate-900 border border-slate-800 hover:border-brand-500 text-slate-400 hover:text-brand-300 transition-all cursor-pointer"
                    >
                      <FileText className="h-3 w-3 text-brand-400" />
                      <span>{cite.filename} (pg. {cite.page})</span>
                      <ChevronDown className={`h-3 w-3 transition-transform ${activeCitations === cite ? 'rotate-180' : ''}`} />
                    </button>
                  ))}
                </div>
              )}

              {/* Expanded Citation Preview */}
              {activeCitations && msg.citations.includes(activeCitations) && (
                <div className="p-3 bg-slate-900/40 border border-slate-800 rounded-xl space-y-2 max-w-md animate-fadeIn">
                  <div className="flex justify-between items-center text-[10px] text-slate-400 border-b border-slate-800/50 pb-1.5">
                    <span className="font-semibold">{activeCitations.filename} - Page {activeCitations.page}</span>
                    <span className="text-brand-400 font-bold uppercase tracking-wider text-[8px] border border-brand-500/20 px-1.5 py-0.5 rounded bg-brand-500/5">Verbatim Quote</span>
                  </div>
                  <p className="text-[10px] text-slate-300 leading-relaxed italic">"{activeCitations.snippet}"</p>
                </div>
              )}
            </div>
          </div>
        ))}
        <div ref={messageEndRef} />
      </div>

      {/* Voice active state visualizer */}
      {isRecording && (
        <div className="h-16 flex items-center justify-center gap-1.5 border-t border-slate-900/60 bg-slate-900/20 px-6">
          <div className="flex items-center gap-2 text-xs font-semibold text-brand-400 animate-pulse-slow">
            <Volume2 className="h-4 w-4" />
            <span>Listening to voice...</span>
          </div>
          {/* Animated audio wave bars */}
          <div className="flex items-end gap-0.5 h-6">
            <span className="w-0.75 bg-brand-500 rounded-full animate-[pulse_0.8s_infinite] h-3" />
            <span className="w-0.75 bg-brand-400 rounded-full animate-[pulse_0.5s_infinite] h-5" />
            <span className="w-0.75 bg-brand-500 rounded-full animate-[pulse_0.7s_infinite] h-2" />
            <span className="w-0.75 bg-brand-400 rounded-full animate-[pulse_0.6s_infinite] h-4" />
          </div>
        </div>
      )}

      {/* Input panel container */}
      <div className="p-4 border-t border-slate-900/80 bg-slate-900/40">
        <form onSubmit={handleSendText} className="flex gap-3 max-w-3xl mx-auto">
          {/* Mic trigger button */}
          <button
            type="button"
            onClick={toggleRecording}
            className={`p-3 rounded-xl flex items-center justify-center cursor-pointer transition-all border
              ${isRecording 
                ? 'bg-rose-500 border-rose-600 text-white animate-pulse' 
                : 'bg-slate-900 border-slate-800 text-slate-400 hover:text-white hover:border-slate-700'}`}
            title={isRecording ? "Stop voice session" : "Start voice session"}
          >
            {isRecording ? <MicOff className="h-5 w-5" /> : <Mic className="h-5 w-5" />}
          </button>

          {/* Text entry fields */}
          <input
            type="text"
            placeholder={isRecording ? "Speak now or type here..." : "Ask a research question..."}
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            disabled={isRecording}
            className="flex-1 bg-slate-900 border border-slate-800 text-xs rounded-xl px-4 focus:outline-none focus:border-brand-500 disabled:opacity-40 text-slate-100 placeholder-slate-500 transition-colors"
          />

          {/* Submit */}
          <button
            type="submit"
            disabled={!inputText.trim() || isRecording}
            className="p-3 bg-brand-600 disabled:opacity-45 hover:bg-brand-500 text-white rounded-xl flex items-center justify-center cursor-pointer transition-colors shadow-lg shadow-brand-600/25"
          >
            <Send className="h-4 w-4" />
          </button>
        </form>
      </div>
    </div>
  )
}
