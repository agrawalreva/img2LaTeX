import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Play, Clock, CheckCircle, XCircle, Loader } from 'lucide-react'

interface TrainingConfig {
  max_steps: number
  learning_rate: number
  batch_size: number
  gradient_accumulation_steps: number
}

interface TrainingJob {
  job_id: string
  status: string
  config: TrainingConfig
  logs: string[]
  artifacts_path?: string
  created_at: string
  updated_at?: string
}

export default function Train() {
  const [config, setConfig] = useState<TrainingConfig>({
    max_steps: 100,
    learning_rate: 2e-4,
    batch_size: 1,
    gradient_accumulation_steps: 4
  })
  const [datasetSize, setDatasetSize] = useState(0)
  const [loading, setLoading] = useState(false)
  const [currentJob, setCurrentJob] = useState<TrainingJob | null>(null)
  const [jobs, setJobs] = useState<TrainingJob[]>([])
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetchDatasetSize()
    fetchJobs()
  }, [])

  useEffect(() => {
    if (currentJob && (currentJob.status === 'QUEUED' || currentJob.status === 'RUNNING')) {
      const interval = setInterval(() => {
        fetchJobStatus(currentJob.job_id)
      }, 2000)
      return () => clearInterval(interval)
    }
  }, [currentJob])

  const fetchDatasetSize = async () => {
    try {
      const response = await fetch('/api/dataset/pairs?limit=1')
      if (response.ok) {
        const data = await response.json()
        setDatasetSize(data.total || 0)
      }
    } catch (err) {
      console.error('Failed to fetch dataset size:', err)
    }
  }

  const fetchJobs = async () => {
    try {
      const response = await fetch('/api/train')
      if (response.ok) {
        const data = await response.json()
        setJobs(data)
        if (data.length > 0) {
          const latest = data[0]
          if (latest.status === 'QUEUED' || latest.status === 'RUNNING') {
            setCurrentJob(latest)
            fetchJobStatus(latest.job_id)
          }
        }
      }
    } catch (err) {
      console.error('Failed to fetch jobs:', err)
    }
  }

  const fetchJobStatus = async (jobId: string) => {
    try {
      const response = await fetch(`/api/train/${jobId}/status`)
      if (response.ok) {
        const job = await response.json()
        setCurrentJob(job)
        setJobs(jobs.map(j => j.job_id === jobId ? job : j))
      }
    } catch (err) {
      console.error('Failed to fetch job status:', err)
    }
  }

  const handleStartTraining = async () => {
    if (datasetSize < 5) {
      setError('Need at least 5 dataset pairs to start training')
      return
    }

    setLoading(true)
    setError(null)

    try {
      const response = await fetch('/api/train', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(config),
      })

      if (!response.ok) {
        const data = await response.json()
        throw new Error(data.detail || 'Failed to start training')
      }

      const data = await response.json()
      setCurrentJob({
        job_id: data.job_id,
        status: data.status,
        config: config,
        logs: [],
        created_at: new Date().toISOString()
      })
      fetchJobs()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to start training')
    } finally {
      setLoading(false)
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'DONE':
        return <CheckCircle className="w-5 h-5 text-emerald-600" />
      case 'FAILED':
        return <XCircle className="w-5 h-5 text-red-600" />
      case 'RUNNING':
        return <Loader className="w-5 h-5 text-blue-600 animate-spin" />
      default:
        return <Clock className="w-5 h-5 text-slate-400" />
    }
  }

  return (
    <div className="max-w-6xl mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-slate-800">Train Model</h1>
        <p className="text-slate-600 mt-2">
          Fine-tune the model on your custom dataset using LoRA
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-white rounded-xl border border-slate-200 p-6"
          >
            <h2 className="text-lg font-semibold text-slate-800 mb-4">Training Configuration</h2>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">
                  Max Steps
                </label>
                <input
                  type="number"
                  value={config.max_steps}
                  onChange={(e) => setConfig({ ...config, max_steps: parseInt(e.target.value) || 100 })}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  min="10"
                  max="1000"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">
                  Learning Rate
                </label>
                <input
                  type="number"
                  step="1e-5"
                  value={config.learning_rate}
                  onChange={(e) => setConfig({ ...config, learning_rate: parseFloat(e.target.value) || 2e-4 })}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  min="1e-5"
                  max="1e-2"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">
                  Batch Size
                </label>
                <input
                  type="number"
                  value={config.batch_size}
                  onChange={(e) => setConfig({ ...config, batch_size: parseInt(e.target.value) || 1 })}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  min="1"
                  max="8"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">
                  Gradient Accumulation Steps
                </label>
                <input
                  type="number"
                  value={config.gradient_accumulation_steps}
                  onChange={(e) => setConfig({ ...config, gradient_accumulation_steps: parseInt(e.target.value) || 4 })}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  min="1"
                  max="16"
                />
              </div>
            </div>

            {error && (
              <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
                {error}
              </div>
            )}

            <button
              onClick={handleStartTraining}
              disabled={loading || datasetSize < 5}
              className="mt-6 w-full px-4 py-3 bg-blue-600 hover:bg-blue-700 disabled:bg-slate-400 text-white rounded-lg font-medium transition-colors flex items-center justify-center"
            >
              {loading ? (
                <>
                  <Loader className="w-5 h-5 mr-2 animate-spin" />
                  Starting...
                </>
              ) : (
                <>
                  <Play className="w-5 h-5 mr-2" />
                  Start Training
                </>
              )}
            </button>

            {datasetSize < 5 && (
              <p className="mt-2 text-sm text-slate-500 text-center">
                Need at least 5 dataset pairs (currently: {datasetSize})
              </p>
            )}
          </motion.div>

          {currentJob && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="bg-white rounded-xl border border-slate-200 p-6"
            >
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-semibold text-slate-800">Current Job</h2>
                <div className="flex items-center space-x-2">
                  {getStatusIcon(currentJob.status)}
                  <span className="text-sm font-medium text-slate-700">{currentJob.status}</span>
                </div>
              </div>

              {currentJob.logs && currentJob.logs.length > 0 && (
                <div className="bg-slate-50 rounded-lg p-4 max-h-64 overflow-y-auto">
                  <pre className="text-xs font-mono text-slate-700 whitespace-pre-wrap">
                    {currentJob.logs.slice(-20).join('\n')}
                  </pre>
                </div>
              )}

              {currentJob.artifacts_path && (
                <div className="mt-4 text-sm text-slate-600">
                  <strong>Artifacts:</strong> {currentJob.artifacts_path}
                </div>
              )}
            </motion.div>
          )}
        </div>

        <div className="lg:col-span-1">
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            className="bg-white rounded-xl border border-slate-200 p-6"
          >
            <h3 className="text-lg font-semibold text-slate-800 mb-4">Training Jobs</h3>
            
            {jobs.length === 0 ? (
              <p className="text-sm text-slate-500">No training jobs yet</p>
            ) : (
              <div className="space-y-3">
                {jobs.map((job) => (
                  <div
                    key={job.job_id}
                    className="p-3 bg-slate-50 rounded-lg border border-slate-200 cursor-pointer hover:bg-slate-100 transition-colors"
                    onClick={() => {
                      setCurrentJob(job)
                      fetchJobStatus(job.job_id)
                    }}
                  >
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-xs font-mono text-slate-600">
                        {job.job_id.substring(0, 8)}...
                      </span>
                      {getStatusIcon(job.status)}
                    </div>
                    <div className="text-xs text-slate-500">
                      {new Date(job.created_at).toLocaleString()}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </motion.div>
        </div>
      </div>
    </div>
  )
} 