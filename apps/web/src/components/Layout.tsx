import { ReactNode, useState } from 'react'
import { History } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'
import HistoryPanel from './HistoryPanel'

interface LayoutProps {
  children: ReactNode
}

interface HistoryItem {
  id: number
  image_path: string
  thumbnail_url: string
  latex: string
  tokens: number
  time_ms: number
  created_at: string
}

export default function Layout({ children }: LayoutProps) {
  const [showHistory, setShowHistory] = useState(false)

  const handleReRun = (item: HistoryItem) => {
  }

  const handleCopyLatex = (latex: string) => {
  }

  return (
    <div className="flex h-screen bg-slate-50">
      {/* Main content area */}
      <div className="flex-1 flex">
        {/* History Panel */}
        <AnimatePresence>
          {showHistory && (
            <motion.div
              initial={{ width: 0, opacity: 0 }}
              animate={{ width: 280, opacity: 1 }}
              exit={{ width: 0, opacity: 0 }}
              className="bg-white border-r border-slate-200 overflow-hidden"
            >
              <HistoryPanel
                onReRun={handleReRun}
                onCopyLatex={handleCopyLatex}
              />
            </motion.div>
          )}
        </AnimatePresence>

        {/* Main content */}
        <div className="flex-1 overflow-auto relative">
          {/* History button in top left */}
          <button
            onClick={() => setShowHistory(!showHistory)}
            className="absolute top-4 left-4 z-10 flex items-center px-3 py-2 bg-white border border-slate-200 rounded-lg shadow-sm hover:bg-slate-50 transition-colors"
          >
            <History className="h-4 w-4 mr-2 text-slate-600" />
            <span className="text-sm font-medium text-slate-700">History</span>
          </button>
          <main className="p-8">{children}</main>
        </div>
      </div>
    </div>
  )
} 