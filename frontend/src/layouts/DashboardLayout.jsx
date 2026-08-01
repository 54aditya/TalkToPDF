import React, { useState, useEffect } from 'react'
import { Link, Outlet, useLocation, useNavigate } from 'react-router-dom'
import { 
  BookOpen, 
  MessageSquare, 
  LogOut, 
  Menu, 
  X, 
  Sparkles, 
  ChevronRight,
  Volume2,
  Trash2
} from 'lucide-react'
import { useAuthStore } from '../store/useAuthStore'
import { useChatStore } from '../store/useChatStore'

export default function DashboardLayout() {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const location = useLocation()
  const navigate = useNavigate()

  const { user, token, logout } = useAuthStore()
  const { sessions, fetchSessions, deleteSession } = useChatStore()

  
  useEffect(() => {
    if (!token) navigate('/login', { replace: true })
  }, [token])

  
  useEffect(() => {
    fetchSessions()
  }, [])

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  const handleDeleteSession = async (e, sessionId) => {
    e.preventDefault()
    e.stopPropagation()
    if (window.confirm('Delete this conversation?')) {
      await deleteSession(sessionId).catch(() => {})
    }
  }

  const isActive = (path) => location.pathname.startsWith(path)

  return (
    <div className="h-screen flex bg-slate-950 overflow-hidden text-slate-100 font-sans">
      
      {sidebarOpen && (
        <div 
          className="fixed inset-0 z-40 bg-slate-950/80 backdrop-blur-sm lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      
      <aside className={`
        fixed inset-y-0 left-0 z-50 w-72 bg-slate-900 border-r border-slate-800/80 flex flex-col transition-transform duration-300 lg:static lg:translate-x-0
        ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'}
      `}>
        
        <div className="h-16 px-6 border-b border-slate-800/80 flex items-center justify-between">
          <Link to="/dashboard" className="flex items-center gap-2.5">
            <div className="p-1.5 bg-brand-600 rounded-lg text-white">
              <Volume2 className="h-5 w-5" />
            </div>
            <span className="font-semibold text-lg tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-white to-slate-400">Voice Research</span>
          </Link>
          <button className="lg:hidden p-1 hover:bg-slate-800 rounded-lg" onClick={() => setSidebarOpen(false)}>
            <X className="h-5 w-5 text-slate-400" />
          </button>
        </div>

        
        <div className="flex-1 overflow-y-auto px-4 py-6 space-y-7">
          
          <div className="space-y-1">
            <Link 
              to="/dashboard"
              onClick={() => setSidebarOpen(false)}
              className={`
                flex items-center justify-between px-3 py-2.5 rounded-xl text-sm font-medium transition-all duration-200
                ${isActive('/dashboard') && !isActive('/chat') 
                  ? 'bg-brand-600/10 text-brand-400 border-l-2 border-brand-500 pl-4' 
                  : 'text-slate-400 hover:bg-slate-800/50 hover:text-slate-200'}
              `}
            >
              <div className="flex items-center gap-3">
                <BookOpen className="h-4 w-4" />
                <span>Paper Library</span>
              </div>
              <ChevronRight className="h-4 w-4 opacity-50" />
            </Link>
          </div>

          
          <div className="space-y-2">
            <div className="flex items-center justify-between px-3">
              <span className="text-[11px] font-bold text-slate-500 uppercase tracking-wider">Voice Conversations</span>
              <Sparkles className="h-3 w-3 text-brand-400" />
            </div>
            
            <div className="space-y-1">
              {sessions.map((session) => (
                <div
                  key={session._id}
                  className={`
                    flex items-center gap-2 px-3 py-2.5 rounded-xl text-xs font-medium transition-all duration-200 group
                    ${location.pathname === `/chat/${session._id}` 
                      ? 'bg-slate-800 text-white' 
                      : 'text-slate-400 hover:bg-slate-800/40 hover:text-slate-200'}
                  `}
                >
                  <Link
                    to={`/chat/${session._id}`}
                    onClick={() => setSidebarOpen(false)}
                    className="flex items-center gap-2 flex-1 min-w-0"
                  >
                    <MessageSquare className="h-3.5 w-3.5 shrink-0 text-slate-500 group-hover:text-brand-400 transition-colors" />
                    <span className="truncate">{session.title}</span>
                  </Link>
                  <button
                    onClick={(e) => handleDeleteSession(e, session._id)}
                    className="opacity-0 group-hover:opacity-100 p-1 hover:text-rose-400 rounded transition-all"
                    title="Delete session"
                  >
                    <Trash2 className="h-3 w-3" />
                  </button>
                </div>
              ))}

              {sessions.length === 0 && (
                <p className="text-[11px] text-slate-500 italic px-3 py-2">No active discussions</p>
              )}
            </div>
          </div>
        </div>

        
        <div className="p-4 border-t border-slate-800/80 bg-slate-900/40">
          <div className="flex items-center justify-between p-2 rounded-xl hover:bg-slate-800/30 transition-all duration-200">
            <div className="flex items-center gap-3 min-w-0">
              <div className="h-9 w-9 bg-brand-500/10 text-brand-400 rounded-lg flex items-center justify-center font-bold text-sm">
                {user?.name?.charAt(0)?.toUpperCase() || 'U'}
              </div>
              <div className="min-w-0">
                <p className="text-xs font-semibold text-slate-200 truncate">{user?.name || 'Guest User'}</p>
                <p className="text-[10px] text-slate-500 truncate">{user?.email || ''}</p>
              </div>
            </div>
            <button 
              onClick={handleLogout}
              className="p-2 hover:bg-red-500/10 hover:text-red-400 rounded-lg text-slate-400 cursor-pointer transition-colors"
              title="Sign Out"
            >
              <LogOut className="h-4 w-4" />
            </button>
          </div>
        </div>
      </aside>

      
      <div className="flex-1 flex flex-col overflow-hidden">
        
        <header className="h-16 border-b border-slate-800/80 bg-slate-900/20 px-6 flex items-center justify-between lg:justify-end">
          <button 
            className="lg:hidden p-2 bg-slate-900 border border-slate-800 rounded-xl hover:bg-slate-800 transition-all"
            onClick={() => setSidebarOpen(true)}
          >
            <Menu className="h-5 w-5 text-slate-300" />
          </button>

          <div className="flex items-center gap-4">
            <div className="flex items-center gap-1.5 text-xs text-emerald-400 bg-emerald-500/10 px-2.5 py-1 rounded-full font-medium">
              <span className="h-1.5 w-1.5 bg-emerald-400 rounded-full animate-pulse" />
              Connected
            </div>
          </div>
        </header>

        
        <main className="flex-1 overflow-y-auto bg-slate-950">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
