import { ReactNode, useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { Home, Database, Train, History } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'
import HistoryPanel from './HistoryPanel'

interface LayoutProps {
  children: ReactNode
}

const navigation = [
  { name: 'Home', href: '/', icon: Home },
  { name: 'Dataset', href: '/dataset', icon: Database },
  { name: 'Train', href: '/train', icon: Train },
]

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
  const location = useLocation()
  const [showHistory, setShowHistory] = useState(true)

  const handleReRun = (item: HistoryItem) => {
    // This will be handled by the parent component
    console.log('Re-run inference for:', item)
  }

  const handleCopyLatex = (latex: string) => {
    // Show toast notification
    console.log('Copied LaTeX:', latex)
  }

  return (
    <div className="flex h-screen bg-slate-50">
      {/* Sidebar */}
      <div className="w-64 bg-white shadow-sm border-r flex flex-col">
        <div className="p-6 border-b border-slate-100">
          <h1 className="text-xl font-bold text-slate-800">VisionLaTeX Studio</h1>
        </div>
        
        <nav className="flex-1 p-4">
          {navigation.map((item) => {
            const isActive = location.pathname === item.href
            return (
              <Link
                key={item.name}
                to={item.href}
                className={`flex items-center px-4 py-3 text-sm font-medium rounded-lg mb-1 transition-colors ${
                  isActive
                    ? 'bg-slate-100 text-slate-800'
                    : 'text-slate-600 hover:bg-slate-50 hover:text-slate-800'
                }`}
              >
                <item.icon className="mr-3 h-5 w-5" />
                {item.name}
              </Link>
            )
          })}
        </nav>

        {/* History Toggle */}
        <div className="p-4 border-t border-slate-100">
          <button
            onClick={() => setShowHistory(!showHistory)}
            className="flex items-center w-full px-4 py-2 text-sm font-medium text-slate-600 hover:bg-slate-50 hover:text-slate-800 rounded-lg transition-colors"
          >
            <History className="mr-3 h-5 w-5" />
            History
          </button>
        </div>
      </div>

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
        <div className="flex-1 overflow-auto">
          <main className="p-8">{children}</main>
        </div>
      </div>
    </div>
  )
} 