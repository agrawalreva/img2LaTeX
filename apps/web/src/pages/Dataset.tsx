import { useState } from 'react'
import { motion } from 'framer-motion'
import { CheckCircle, AlertCircle } from 'lucide-react'
import DatasetTable from '../components/DatasetTable'

export default function Dataset() {
  const [toast, setToast] = useState<{ type: 'success' | 'error'; message: string } | null>(null)

  const handleExport = (format: 'csv' | 'jsonl') => {
    // In a real implementation, this would fetch the data and create a download
    console.log(`Exporting dataset as ${format}`)
    
    setToast({
      type: 'success',
      message: `Dataset exported as ${format.toUpperCase()}`
    })
    
    setTimeout(() => setToast(null), 3000)
  }

  return (
    <div className="max-w-7xl mx-auto">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="mb-8"
      >
        <h1 className="text-3xl font-bold text-slate-800 mb-2">Dataset Management</h1>
        <p className="text-slate-600">
          Manage your image-LaTeX pairs for training and export datasets
        </p>
      </motion.div>

      {/* Dataset Table */}
      <DatasetTable onExport={handleExport} />

      {/* Toast Notifications */}
      {toast && (
        <motion.div
          initial={{ opacity: 0, y: 50 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: 50 }}
          className={`fixed bottom-4 right-4 p-4 rounded-lg shadow-lg flex items-center space-x-2 ${
            toast.type === 'success' 
              ? 'bg-emerald-50 border border-emerald-200 text-emerald-800'
              : 'bg-red-50 border border-red-200 text-red-800'
          }`}
        >
          {toast.type === 'success' ? (
            <CheckCircle className="w-5 h-5" />
          ) : (
            <AlertCircle className="w-5 h-5" />
          )}
          <span className="font-medium">{toast.message}</span>
        </motion.div>
      )}
    </div>
  )
} 