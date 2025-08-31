import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Edit3, Save, X, Download, Image as ImageIcon, CheckCircle } from 'lucide-react'

interface DatasetPair {
  id: number
  image_path: string
  latex_text: string
  is_corrected: boolean
  created_at: string
  updated_at?: string
}

interface DatasetTableProps {
  onExport: (format: 'csv' | 'jsonl') => void
}

export default function DatasetTable({ onExport }: DatasetTableProps) {
  const [pairs, setPairs] = useState<DatasetPair[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [editingId, setEditingId] = useState<number | null>(null)
  const [editText, setEditText] = useState('')
  const [saving, setSaving] = useState<number | null>(null)

  const fetchPairs = async () => {
    try {
      setLoading(true)
      const response = await fetch('/api/dataset/pairs?limit=50')
      if (!response.ok) {
        throw new Error('Failed to fetch dataset')
      }
      const data = await response.json()
      setPairs(data.pairs)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load dataset')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchPairs()
  }, [])

  const handleEdit = (pair: DatasetPair) => {
    setEditingId(pair.id)
    setEditText(pair.latex_text)
  }

  const handleSave = async (id: number) => {
    try {
      setSaving(id)
      const response = await fetch(`/api/dataset/pairs/${id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ latex_text: editText }),
      })

      if (!response.ok) {
        throw new Error('Failed to update pair')
      }

      // Update local state
      setPairs(pairs.map(pair => 
        pair.id === id 
          ? { ...pair, latex_text: editText, is_corrected: true }
          : pair
      ))
      setEditingId(null)
      setEditText('')
    } catch (err) {
      console.error('Failed to save:', err)
    } finally {
      setSaving(null)
    }
  }

  const handleCancel = () => {
    setEditingId(null)
    setEditText('')
  }

  const formatDate = (isoString: string) => {
    return new Date(isoString).toLocaleDateString()
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-slate-600"></div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <p className="text-slate-600 mb-4">{error}</p>
        <button
          onClick={fetchPairs}
          className="px-4 py-2 bg-slate-600 text-white rounded-lg hover:bg-slate-700 transition-colors"
        >
          Try Again
        </button>
      </div>
    )
  }

  if (pairs.length === 0) {
    return (
      <div className="text-center py-12">
        <ImageIcon className="w-12 h-12 mx-auto mb-4 text-slate-300" />
        <h3 className="text-lg font-medium text-slate-600 mb-2">No dataset pairs yet</h3>
        <p className="text-slate-500">Start by generating LaTeX from images to build your dataset</p>
      </div>
    )
  }

  return (
    <div className="bg-white rounded-xl border border-slate-200 overflow-hidden">
      {/* Header */}
      <div className="flex items-center justify-between p-6 border-b border-slate-100">
        <div>
          <h2 className="text-lg font-semibold text-slate-800">Dataset Pairs</h2>
          <p className="text-sm text-slate-500 mt-1">
            {pairs.length} pairs • {pairs.filter(p => p.is_corrected).length} corrected
          </p>
        </div>
        
        <div className="flex space-x-2">
          <button
            onClick={() => onExport('csv')}
            className="px-3 py-2 text-sm bg-slate-100 text-slate-700 rounded-lg hover:bg-slate-200 transition-colors"
          >
            <Download className="w-4 h-4 mr-1 inline" />
            Export CSV
          </button>
          <button
            onClick={() => onExport('jsonl')}
            className="px-3 py-2 text-sm bg-slate-100 text-slate-700 rounded-lg hover:bg-slate-200 transition-colors"
          >
            <Download className="w-4 h-4 mr-1 inline" />
            Export JSONL
          </button>
        </div>
      </div>

      {/* Table */}
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead className="bg-slate-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">
                Image
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">
                LaTeX
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">
                Status
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">
                Date
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">
                Actions
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-200">
            {pairs.map((pair) => (
              <motion.tr
                key={pair.id}
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="hover:bg-slate-50"
              >
                {/* Image */}
                <td className="px-6 py-4">
                  <div className="w-16 h-16 bg-slate-100 rounded-lg flex items-center justify-center">
                    <ImageIcon className="w-6 h-6 text-slate-400" />
                  </div>
                </td>

                {/* LaTeX */}
                <td className="px-6 py-4">
                  {editingId === pair.id ? (
                    <div className="space-y-2">
                      <textarea
                        value={editText}
                        onChange={(e) => setEditText(e.target.value)}
                        className="w-full p-2 text-sm font-mono border border-slate-300 rounded-md focus:ring-2 focus:ring-slate-500 focus:border-transparent"
                        rows={3}
                      />
                      <div className="flex space-x-2">
                        <button
                          onClick={() => handleSave(pair.id)}
                          disabled={saving === pair.id}
                          className="px-2 py-1 text-xs bg-emerald-600 text-white rounded hover:bg-emerald-700 disabled:opacity-50"
                        >
                          {saving === pair.id ? 'Saving...' : 'Save'}
                        </button>
                        <button
                          onClick={handleCancel}
                          className="px-2 py-1 text-xs bg-slate-300 text-slate-700 rounded hover:bg-slate-400"
                        >
                          Cancel
                        </button>
                      </div>
                    </div>
                  ) : (
                    <div className="max-w-md">
                      <pre className="text-sm font-mono text-slate-800 bg-slate-50 p-2 rounded border">
                        {pair.latex_text}
                      </pre>
                    </div>
                  )}
                </td>

                {/* Status */}
                <td className="px-6 py-4">
                  {pair.is_corrected ? (
                    <span className="inline-flex items-center px-2 py-1 text-xs font-medium bg-emerald-100 text-emerald-800 rounded-full">
                      <CheckCircle className="w-3 h-3 mr-1" />
                      Corrected
                    </span>
                  ) : (
                    <span className="inline-flex items-center px-2 py-1 text-xs font-medium bg-slate-100 text-slate-800 rounded-full">
                      Original
                    </span>
                  )}
                </td>

                {/* Date */}
                <td className="px-6 py-4 text-sm text-slate-500">
                  {formatDate(pair.created_at)}
                </td>

                {/* Actions */}
                <td className="px-6 py-4">
                  {editingId !== pair.id && (
                    <button
                      onClick={() => handleEdit(pair)}
                      className="p-1 text-slate-400 hover:text-slate-600 transition-colors"
                    >
                      <Edit3 className="w-4 h-4" />
                    </button>
                  )}
                </td>
              </motion.tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
