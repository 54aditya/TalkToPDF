import React, { useState } from 'react'
import { Link, Outlet, useLocation, useNavigate } from 'react-router-dom'
import { 
  BookOpen, 
  MessageSquare, 
  LogOut, 
  Menu, 
  X, 
  Sparkles, 
  ChevronRight,
  Database,
  Volume2
} from 'lucide-react'

export default function DashboardLayout() {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const location = useLocation()
  const navigate = useNavigate()

  // Mocked state for navigation - this will connect to stores in future phases.
  const activeChats = [
    { id: '1', title: 'Attention Mechanism in Transformers' },
    { id: '2', title: 'ResNet ResBlocks and Gradients' }
  ]

  const handleLogout = () => {
    navigate('/login')
  }

  const isActive = (path) => location.pathname.startsWith(path)

  return (
    <div className="h-screen flex bg-slate-950 overflow-hidden text-slate-100 font-sans">
      {/* Mobile Sidebar Overlay */}
      {sidebarOpen && (
        <div 
          className="fixed inset-0 z-40 bg-slate-950/80 backdrop-blur-sm lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar Component */}
      <aside className={`
        fixed inset-y-0 left-0 z-50 w-72 bg-slate-900 border-r border-slate-800/80 flex flex-col transition-transform duration-300 lg:static lg:translate-x-0
        ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'}
      `}>
        {/* Header/Logo */}
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

        {/* Scrollable Navigation */}
        <div className="flex-1 overflow-y-auto px-4 py-6 space-y-7">
          {/* Main Navigation */}
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

          {/* Chat History Section */}
          <div className="space-y-2">
            <div className="flex items-center justify-between px-3">
              <span className="text-[11px] font-bold text-slate-500 uppercase tracking-wider">Voice Conversations</span>
              <Sparkles className="h-3 w-3 text-brand-400" />
            </div>
            
            <div className="space-y-1">
              {activeChats.map((chat) => (
                <Link
                  key={chat.id}
                  to={`/chat/${chat.id}`}
                  onClick={() => setSidebarOpen(false)}
                  className={`
                    flex items-center gap-3 px-3 py-2.5 rounded-xl text-xs font-medium transition-all duration-200 truncate group
                    ${location.pathname === `/chat/${chat.id}` 
                      ? 'bg-slate-800 text-white' 
                      : 'text-slate-400 hover:bg-slate-800/40 hover:text-slate-200'}
                  `}
                >
                  <MessageSquare className="h-3.5 w-3.5 shrink-0 text-slate-500 group-hover:text-brand-400 transition-colors" />
                  <span className="truncate">{chat.title}</span>
                </Link>
              ))}

              {activeChats.length === 0 && (
                <p className="text-[11px] text-slate-500 italic px-3 py-2">No active discussions</p>
              )}
            </div>
          </div>
        </div>

        {/* Footer/User Info */}
        <div className="p-4 border-t border-slate-800/80 bg-slate-900/40">
          <div className="flex items-center justify-between p-2 rounded-xl hover:bg-slate-800/30 transition-all duration-200">
            <div className="flex items-center gap-3 min-w-0">
              <div className="h-9 w-9 bg-brand-500/10 text-brand-400 rounded-lg flex items-center justify-center font-bold">
                JD
              </div>
              <div className="min-w-0">
                <p className="text-xs font-semibold text-slate-200 truncate">John Doe</p>
                <p className="text-[10px] text-slate-500 truncate">john.doe@example.com</p>
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

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Navbar */}
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

        {/* Main Work Area */}
        <main className="flex-1 overflow-y-auto bg-slate-950">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
