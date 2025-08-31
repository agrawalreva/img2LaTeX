import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Clock, Copy, RefreshCw, Image as ImageIcon } from 'lucide-react'

interface HistoryItem {
  id: number
  image_path: string
  thumbnail_url: string
  latex: string
  tokens: number
  time_ms: number
  created_at: string
}

interface HistoryPanelProps {
  onReRun: (item: HistoryItem) => void
  onCopyLatex: (latex: string) => void
}

export default function HistoryPanel({ onReRun, onCopyLatex }: HistoryPanelProps) {
  const [history, setHistory] = useState<HistoryItem[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchHistory = async () => {
    try {
      setLoading(true)
      const response = await fetch('/api/history?limit=20')
      if (!response.ok) {
        throw new Error('Failed to fetch history')
      }
      const data = await response.json()
      setHistory(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load history')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchHistory()
  }, [])

  const formatTime = (isoString: string) => {
    const date = new Date(isoString)
    const now = new Date()
    const diffMs = now.getTime() - date.getTime()
    const diffMins = Math.floor(diffMs / 60000)
    const diffHours = Math.floor(diffMs / 3600000)
    const diffDays = Math.floor(diffMs / 86400000)

    if (diffMins < 1) return 'Just now'
    if (diffMins < 60) return `${diffMins}m ago`
    if (diffHours < 24) return `${diffHours}h ago`
    return `${diffDays}d ago`
  }

  const handleCopyLatex = async (latex: string) => {
    try {
      await navigator.clipboard.writeText(latex)
      onCopyLatex(latex)
    } catch (err) {
      console.error('Failed to copy:', err)
    }
  }

  if (loading) {
    return (
      <div className="p-4">
        <div className="flex items-center justify-center py-8">
          <RefreshCw className="w-5 h-5 animate-spin text-slate-400" />
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="p-4">
        <div className="text-center py-8 text-slate-500">
          <p className="text-sm">{error}</p>
          <button
            onClick={fetchHistory}
            className="mt-2 text-xs text-slate-400 hover:text-slate-600"
          >
            Try again
          </button>
        </div>
      </div>
    )
  }

  if (history.length === 0) {
    return (
      <div className="p-4">
        <div className="text-center py-8 text-slate-500">
          <ImageIcon className="w-8 h-8 mx-auto mb-2 text-slate-300" />
          <p className="text-sm">No history yet</p>
          <p className="text-xs text-slate-400">Upload an image to get started</p>
        </div>
      </div>
    )
  }

  return (
    <div className="p-4">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-medium text-slate-700">Recent Inferences</h3>
        <button
          onClick={fetchHistory}
          className="p-1 text-slate-400 hover:text-slate-600 transition-colors"
        >
          <RefreshCw className="w-4 h-4" />
        </button>
      </div>

      <div className="space-y-3">
        <AnimatePresence>
          {history.map((item, index) => (
            <motion.div
              key={item.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ delay: index * 0.05 }}
              className="bg-white rounded-lg border border-slate-200 p-3 hover:shadow-sm transition-shadow cursor-pointer group"
              onClick={() => onReRun(item)}
            >
              {/* Thumbnail */}
              <div className="relative mb-3">
                <div className="w-full h-20 bg-slate-100 rounded-md flex items-center justify-center">
                  <ImageIcon className="w-6 h-6 text-slate-400" />
                </div>
                <div className="absolute inset-0 bg-slate-900/10 opacity-0 group-hover:opacity-100 transition-opacity rounded-md" />
              </div>

              {/* LaTeX Preview */}
              <div className="mb-2">
                <p className="text-xs font-mono text-slate-600 line-clamp-2">
                  {item.latex}
                </p>
              </div>

              {/* Metadata */}
              <div className="flex items-center justify-between text-xs text-slate-500">
                <div className="flex items-center space-x-2">
                  <Clock className="w-3 h-3" />
                  <span>{formatTime(item.created_at)}</span>
                </div>
                
                <div className="flex items-center space-x-1">
                  <button
                    onClick={(e) => {
                      e.stopPropagation()
                      handleCopyLatex(item.latex)
                    }}
                    className="p-1 text-slate-400 hover:text-slate-600 transition-colors"
                  >
                    <Copy className="w-3 h-3" />
                  </button>
                </div>
              </div>
            </motion.div>
          ))}
        </AnimatePresence>
      </div>
    </div>
  )
}
