import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { 
  UploadCloud, 
  FileText, 
  Trash2, 
  MessageSquareShare, 
  Search, 
  Layers,
  Database,
  Calendar
} from 'lucide-react'

export default function Dashboard() {
  const navigate = useNavigate()
  const [searchQuery, setSearchQuery] = useState('')
  const [dragging, setDragging] = useState(false)
  const [uploading, setUploading] = useState(false)
  const [uploadProgress, setUploadProgress] = useState(0)

  // Mock document database
  const [documents, setDocuments] = useState([
    { id: '1', filename: 'Attention_Is_All_You_Need.pdf', size: '2.1 MB', pages: 15, status: 'processed', date: '2026-07-28' },
    { id: '2', filename: 'ResNet_Deep_Residual_Learning.pdf', size: '4.8 MB', pages: 12, status: 'processed', date: '2026-07-27' },
    { id: '3', filename: 'GPT4_Technical_Report.pdf', size: '12.4 MB', pages: 98, status: 'processing', date: '2026-07-29' },
    { id: '4', filename: 'BERT_Pretraining_of_Transformers.pdf', size: '1.2 MB', pages: 16, status: 'failed', date: '2026-07-25' }
  ])

  const handleDragOver = (e) => {
    e.preventDefault()
    setDragging(true)
  }

  const handleDragLeave = () => {
    setDragging(false)
  }

  const handleDrop = (e) => {
    e.preventDefault()
    setDragging(false)
    const files = e.dataTransfer.files
    if (files.length > 0) {
      simulateUpload(files[0].name)
    }
  }

  const handleFileSelect = (e) => {
    const files = e.target.files
    if (files.length > 0) {
      simulateUpload(files[0].name)
    }
  }

  const simulateUpload = (name) => {
    setUploading(true)
    setUploadProgress(0)
    const interval = setInterval(() => {
      setUploadProgress((prev) => {
        if (prev >= 100) {
          clearInterval(interval)
          setUploading(false)
          setDocuments((old) => [
            {
              id: String(old.length + 1),
              filename: name,
              size: '4.5 MB',
              pages: 32,
              status: 'processed',
              date: new Date().toISOString().split('T')[0]
            },
            ...old
          ])
          return 100
        }
        return prev + 10
      })
    }, 150)
  }

  const handleDelete = (id) => {
    setDocuments(documents.filter(doc => doc.id !== id))
  }

  const handleStartChat = (doc) => {
    // Navigate to a new chat with this document initialized
    navigate(`/chat/${doc.id}`)
  }

  const filteredDocs = documents.filter(doc => 
    doc.filename.toLowerCase().includes(searchQuery.toLowerCase())
  )

  return (
    <div className="p-6 max-w-6xl mx-auto space-y-8">
      {/* Page Header */}
      <div>
        <h1 className="text-3xl font-extrabold tracking-tight">Research Paper Library</h1>
        <p className="text-sm text-slate-400 mt-1">Upload research documents, parse mathematical concepts, and chat via voice.</p>
      </div>

      {/* Drag & Drop Upload Zone */}
      <div 
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        className={`
          border-2 border-dashed rounded-2xl p-10 flex flex-col items-center justify-center text-center transition-all duration-300 relative
          ${dragging ? 'border-brand-500 bg-brand-500/5' : 'border-slate-800 bg-slate-900/20 hover:border-slate-700'}
        `}
      >
        <input 
          type="file" 
          id="file-upload" 
          multiple 
          accept=".pdf" 
          onChange={handleFileSelect} 
          className="hidden" 
        />
        <label htmlFor="file-upload" className="cursor-pointer flex flex-col items-center">
          <div className="p-4 bg-slate-900 border border-slate-800 rounded-2xl text-slate-400 mb-4 hover:scale-105 hover:text-brand-400 hover:border-brand-500/40 transition-all duration-200">
            <UploadCloud className="h-8 w-8" />
          </div>
          <span className="text-sm font-semibold">Drag & drop your research PDF here, or <span className="text-brand-400 hover:underline">browse</span></span>
          <span className="text-xs text-slate-500 mt-2">Supports academic PDFs up to 50MB</span>
        </label>

        {uploading && (
          <div className="absolute inset-0 bg-slate-950/90 rounded-2xl flex flex-col items-center justify-center p-6 backdrop-blur-sm z-20">
            <div className="w-full max-w-xs space-y-3">
              <div className="flex justify-between items-center text-xs font-semibold">
                <span>Uploading and extracting text...</span>
                <span>{uploadProgress}%</span>
              </div>
              <div className="h-2 w-full bg-slate-800 rounded-full overflow-hidden">
                <div 
                  className="h-full bg-brand-500 rounded-full transition-all duration-150"
                  style={{ width: `${uploadProgress}%` }}
                />
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Document Library Directory */}
      <div className="space-y-4">
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
          <h2 className="text-lg font-bold flex items-center gap-2">
            <Layers className="h-5 w-5 text-brand-400" />
            <span>Uploaded Publications ({filteredDocs.length})</span>
          </h2>
          {/* Search bar */}
          <div className="relative w-full sm:w-64">
            <Search className="absolute left-3 top-2.5 h-4 w-4 text-slate-500" />
            <input
              type="text"
              placeholder="Search library..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-9 pr-4 py-2 bg-slate-900/60 border border-slate-800 rounded-xl text-xs focus:outline-none focus:border-brand-500 text-slate-200 placeholder-slate-500 transition-colors"
            />
          </div>
        </div>

        {/* Desktop Documents Table */}
        <div className="glass border border-slate-800 rounded-xl overflow-hidden shadow-xl">
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-slate-800 text-[11px] font-bold text-slate-400 uppercase bg-slate-900/50">
                  <th className="px-6 py-4">Filename</th>
                  <th className="px-6 py-4">Size</th>
                  <th className="px-6 py-4">Pages</th>
                  <th className="px-6 py-4">Status</th>
                  <th className="px-6 py-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 text-xs">
                {filteredDocs.map((doc) => (
                  <tr key={doc.id} className="hover:bg-slate-900/20 transition-colors group">
                    <td className="px-6 py-4 font-semibold text-slate-200 flex items-center gap-3">
                      <FileText className="h-4 w-4 text-brand-400" />
                      <span className="truncate max-w-xs sm:max-w-md">{doc.filename}</span>
                    </td>
                    <td className="px-6 py-4 text-slate-400">{doc.size}</td>
                    <td className="px-6 py-4 text-slate-400">{doc.pages} pgs</td>
                    <td className="px-6 py-4">
                      {doc.status === 'processed' && (
                        <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[10px] font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                          Ready
                        </span>
                      )}
                      {doc.status === 'processing' && (
                        <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[10px] font-semibold bg-amber-500/10 text-amber-400 border border-amber-500/20 animate-pulse">
                          Parsing
                        </span>
                      )}
                      {doc.status === 'failed' && (
                        <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[10px] font-semibold bg-rose-500/10 text-rose-400 border border-rose-500/20">
                          Error
                        </span>
                      )}
                    </td>
                    <td className="px-6 py-4 text-right">
                      <div className="flex justify-end gap-2 opacity-80 group-hover:opacity-100 transition-opacity">
                        <button
                          onClick={() => handleStartChat(doc)}
                          disabled={doc.status !== 'processed'}
                          className="p-1.5 bg-brand-600/10 hover:bg-brand-600 hover:text-white text-brand-400 rounded-lg disabled:opacity-30 disabled:hover:bg-brand-600/10 disabled:hover:text-brand-400 cursor-pointer transition-colors"
                          title="Start Conversation"
                        >
                          <MessageSquareShare className="h-4 w-4" />
                        </button>
                        <button
                          onClick={() => handleDelete(doc.id)}
                          className="p-1.5 bg-slate-900 border border-slate-800 text-slate-400 hover:text-rose-400 hover:border-rose-900 rounded-lg cursor-pointer transition-colors"
                          title="Delete Paper"
                        >
                          <Trash2 className="h-4 w-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}

                {filteredDocs.length === 0 && (
                  <tr>
                    <td colSpan="5" className="px-6 py-10 text-center text-slate-500 italic">
                      No research papers found in library.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  )
}
