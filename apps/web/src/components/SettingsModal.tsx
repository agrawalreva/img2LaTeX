import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { X, Settings, Zap, Brain, CheckCircle } from 'lucide-react'

interface SettingsModalProps {
  isOpen: boolean
  onClose: () => void
}

interface Adapter {
  job_id: string
  path: string
  config: any
  created_at: number
}

interface GenerationSettings {
  max_new_tokens: number
  temperature: number
  min_p: number
}

export default function SettingsModal({ isOpen, onClose }: SettingsModalProps) {
  const [currentModel, setCurrentModel] = useState<any>(null)
  const [adapters, setAdapters] = useState<Adapter[]>([])
  const [settings, setSettings] = useState<GenerationSettings>({
    max_new_tokens: 256,
    temperature: 0.7,
    min_p: 0.1
  })
  const [loading, setLoading] = useState(false)
  const [switching, setSwitching] = useState(false)

  useEffect(() => {
    if (isOpen) {
      fetchCurrentModel()
      fetchAdapters()
      fetchSettings()
    }
  }, [isOpen])

  const fetchCurrentModel = async () => {
    try {
      const response = await fetch('/api/models/current')
      if (response.ok) {
        const data = await response.json()
        setCurrentModel(data)
      }
    } catch (err) {
      console.error('Failed to fetch current model:', err)
    }
  }

  const fetchAdapters = async () => {
    try {
      const response = await fetch('/api/models/adapters')
      if (response.ok) {
        const data = await response.json()
        setAdapters(data)
      }
    } catch (err) {
      console.error('Failed to fetch adapters:', err)
    }
  }

  const fetchSettings = async () => {
    try {
      const response = await fetch('/api/models/settings')
      if (response.ok) {
        const data = await response.json()
        setSettings(data)
      }
    } catch (err) {
      console.error('Failed to fetch settings:', err)
    }
  }

  const switchModel = async (adapterPath: string) => {
    try {
      setSwitching(true)
      const response = await fetch('/api/models/switch', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ adapter_path: adapterPath }),
      })

      if (response.ok) {
        await fetchCurrentModel()
        // Show success feedback
        setTimeout(() => setSwitching(false), 1000)
      } else {
        throw new Error('Failed to switch model')
      }
    } catch (err) {
      console.error('Failed to switch model:', err)
      setSwitching(false)
    }
  }

  const updateSettings = async (newSettings: GenerationSettings) => {
    try {
      const response = await fetch('/api/models/settings', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(newSettings),
      })

      if (response.ok) {
        setSettings(newSettings)
        // Show success feedback
      }
    } catch (err) {
      console.error('Failed to update settings:', err)
    }
  }

  const formatDate = (timestamp: number) => {
    return new Date(timestamp * 1000).toLocaleDateString()
  }

  if (!isOpen) return null

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4"
        onClick={onClose}
      >
        <motion.div
          initial={{ scale: 0.95, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          exit={{ scale: 0.95, opacity: 0 }}
          className="bg-white rounded-xl shadow-xl max-w-2xl w-full max-h-[90vh] overflow-hidden"
          onClick={(e) => e.stopPropagation()}
        >
          {/* Header */}
          <div className="flex items-center justify-between p-6 border-b border-slate-200">
            <div className="flex items-center space-x-3">
              <Settings className="w-6 h-6 text-slate-600" />
              <h2 className="text-xl font-semibold text-slate-800">Settings</h2>
            </div>
            <button
              onClick={onClose}
              className="p-2 text-slate-400 hover:text-slate-600 transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          <div className="p-6 space-y-6 max-h-[calc(90vh-120px)] overflow-y-auto">
            {/* Current Model */}
            <div className="space-y-3">
              <h3 className="text-lg font-medium text-slate-800 flex items-center">
                <Brain className="w-5 h-5 mr-2" />
                Current Model
              </h3>
              <div className="bg-slate-50 rounded-lg p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium text-slate-800">
                      {currentModel?.name || 'Loading...'}
                    </p>
                    <p className="text-sm text-slate-500">
                      {currentModel?.type === 'adapter' ? 'Fine-tuned adapter' : 'Base model'}
                    </p>
                  </div>
                  {currentModel?.type === 'adapter' && (
                    <button
                      onClick={() => switchModel('base')}
                      disabled={switching}
                      className="px-3 py-1.5 text-sm bg-slate-200 text-slate-700 rounded-lg hover:bg-slate-300 transition-colors disabled:opacity-50"
                    >
                      {switching ? 'Switching...' : 'Switch to Base'}
                    </button>
                  )}
                </div>
              </div>
            </div>

            {/* Available Adapters */}
            {adapters.length > 0 && (
              <div className="space-y-3">
                <h3 className="text-lg font-medium text-slate-800 flex items-center">
                  <Zap className="w-5 h-5 mr-2" />
                  Available Adapters
                </h3>
                <div className="space-y-2">
                  {adapters.map((adapter) => (
                    <div
                      key={adapter.job_id}
                      className="bg-slate-50 rounded-lg p-4 border border-slate-200"
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex-1">
                          <p className="font-medium text-slate-800">
                            {adapter.job_id[:8]}...
                          </p>
                          <p className="text-sm text-slate-500">
                            Created: {formatDate(adapter.created_at)}
                          </p>
                          {adapter.config && (
                            <p className="text-xs text-slate-400 mt-1">
                              Steps: {adapter.config.get('max_steps', 'N/A')} | 
                              LR: {adapter.config.get('learning_rate', 'N/A')}
                            </p>
                          )}
                        </div>
                        <button
                          onClick={() => switchModel(adapter.path)}
                          disabled={switching}
                          className="px-3 py-1.5 text-sm bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 transition-colors disabled:opacity-50"
                        >
                          {switching ? 'Switching...' : 'Use'}
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Generation Settings */}
            <div className="space-y-3">
              <h3 className="text-lg font-medium text-slate-800 flex items-center">
                <Zap className="w-5 h-5 mr-2" />
                Generation Settings
              </h3>
              <div className="space-y-4">
                {/* Max Tokens */}
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">
                    Max New Tokens
                  </label>
                  <input
                    type="number"
                    min="1"
                    max="1024"
                    value={settings.max_new_tokens}
                    onChange={(e) => {
                      const newSettings = { ...settings, max_new_tokens: parseInt(e.target.value) }
                      setSettings(newSettings)
                      updateSettings(newSettings)
                    }}
                    className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-slate-500 focus:border-transparent"
                  />
                </div>

                {/* Temperature */}
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">
                    Temperature
                  </label>
                  <input
                    type="number"
                    min="0.0"
                    max="2.0"
                    step="0.1"
                    value={settings.temperature}
                    onChange={(e) => {
                      const newSettings = { ...settings, temperature: parseFloat(e.target.value) }
                      setSettings(newSettings)
                      updateSettings(newSettings)
                    }}
                    className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-slate-500 focus:border-transparent"
                  />
                </div>

                {/* Min P */}
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">
                    Min P
                  </label>
                  <input
                    type="number"
                    min="0.0"
                    max="1.0"
                    step="0.1"
                    value={settings.min_p}
                    onChange={(e) => {
                      const newSettings = { ...settings, min_p: parseFloat(e.target.value) }
                      setSettings(newSettings)
                      updateSettings(newSettings)
                    }}
                    className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-slate-500 focus:border-transparent"
                  />
                </div>
              </div>
            </div>
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  )
}
