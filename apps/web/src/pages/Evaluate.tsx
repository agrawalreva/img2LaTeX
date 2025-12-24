import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Play, CheckCircle, XCircle, TrendingUp } from 'lucide-react'

interface SampleImage {
  id: string
  name: string
  description: string
  url: string
  expected_latex: string
}

interface EvaluationResult {
  image_path: string
  ground_truth: string
  predicted: string | null
  similarity: number
  exact_match: boolean
  tokens?: number
  time_ms?: number
  error?: string
}

interface EvaluationResponse {
  total: number
  exact_matches: number
  accuracy: number
  average_similarity: number
  results: EvaluationResult[]
}

export default function Evaluate() {
  const [samples, setSamples] = useState<SampleImage[]>([])
  const [loading, setLoading] = useState(false)
  const [results, setResults] = useState<EvaluationResponse | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetchSamples()
  }, [])

  const fetchSamples = async () => {
    try {
      const response = await fetch('/api/sample-images')
      if (response.ok) {
        const data = await response.json()
        setSamples(data.sample_images || [])
      }
    } catch (err) {
      console.error('Failed to fetch samples:', err)
    }
  }

  const handleEvaluate = async () => {
    if (samples.length === 0) {
      setError('No sample images available')
      return
    }

    setLoading(true)
    setError(null)
    setResults(null)

    try {
      const pairs = samples.map(sample => ({
        image_path: sample.url,
        ground_truth: sample.expected_latex
      }))

      const response = await fetch('/api/evaluate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ pairs }),
      })

      if (!response.ok) {
        const data = await response.json()
        throw new Error(data.detail || 'Evaluation failed')
      }

      const data = await response.json()
      setResults(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Evaluation failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-6xl mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-slate-800">Model Evaluation</h1>
        <p className="text-slate-600 mt-2">
          Evaluate model performance on sample equations
        </p>
      </div>

      <div className="space-y-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-white rounded-xl border border-slate-200 p-6"
        >
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-lg font-semibold text-slate-800">Sample Images</h2>
              <p className="text-sm text-slate-500 mt-1">
                {samples.length} sample equations available
              </p>
            </div>
            <button
              onClick={handleEvaluate}
              disabled={loading || samples.length === 0}
              className="px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-slate-400 text-white rounded-lg font-medium transition-colors flex items-center"
            >
              {loading ? (
                <>
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2" />
                  Evaluating...
                </>
              ) : (
                <>
                  <Play className="w-4 h-4 mr-2" />
                  Run Evaluation
                </>
              )}
            </button>
          </div>

          {error && (
            <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
              {error}
            </div>
          )}

          {results && (
            <div className="mt-6 grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-slate-50 rounded-lg p-4">
                <div className="text-sm text-slate-600 mb-1">Accuracy</div>
                <div className="text-2xl font-bold text-slate-800">
                  {(results.accuracy * 100).toFixed(1)}%
                </div>
                <div className="text-xs text-slate-500 mt-1">
                  {results.exact_matches} / {results.total} exact matches
                </div>
              </div>
              <div className="bg-slate-50 rounded-lg p-4">
                <div className="text-sm text-slate-600 mb-1">Avg Similarity</div>
                <div className="text-2xl font-bold text-slate-800">
                  {(results.average_similarity * 100).toFixed(1)}%
                </div>
                <div className="text-xs text-slate-500 mt-1">
                  Sequence similarity score
                </div>
              </div>
              <div className="bg-slate-50 rounded-lg p-4">
                <div className="text-sm text-slate-600 mb-1">Total Samples</div>
                <div className="text-2xl font-bold text-slate-800">
                  {results.total}
                </div>
                <div className="text-xs text-slate-500 mt-1">
                  Test cases evaluated
                </div>
              </div>
            </div>
          )}
        </motion.div>

        {results && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-white rounded-xl border border-slate-200 p-6"
          >
            <h2 className="text-lg font-semibold text-slate-800 mb-4">Detailed Results</h2>
            <div className="space-y-4">
              {results.results.map((result, idx) => {
                const sample = samples.find(s => s.url === result.image_path)
                return (
                  <div
                    key={idx}
                    className="border border-slate-200 rounded-lg p-4"
                  >
                    <div className="flex items-start justify-between mb-3">
                      <div>
                        <h3 className="font-medium text-slate-800">
                          {sample?.name || 'Unknown'}
                        </h3>
                        <p className="text-xs text-slate-500 mt-1">
                          {sample?.description}
                        </p>
                      </div>
                      <div className="flex items-center space-x-2">
                        {result.exact_match ? (
                          <CheckCircle className="w-5 h-5 text-emerald-600" />
                        ) : (
                          <XCircle className="w-5 h-5 text-red-600" />
                        )}
                        <span className="text-sm font-medium text-slate-700">
                          {(result.similarity * 100).toFixed(1)}%
                        </span>
                      </div>
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                      <div>
                        <div className="text-slate-600 mb-1">Ground Truth</div>
                        <pre className="bg-slate-50 p-2 rounded font-mono text-xs text-slate-800 overflow-x-auto">
                          {result.ground_truth}
                        </pre>
                      </div>
                      <div>
                        <div className="text-slate-600 mb-1">Predicted</div>
                        <pre className="bg-slate-50 p-2 rounded font-mono text-xs text-slate-800 overflow-x-auto">
                          {result.predicted || result.error || 'N/A'}
                        </pre>
                      </div>
                    </div>
                    {result.tokens && result.time_ms && (
                      <div className="mt-2 text-xs text-slate-500">
                        {result.tokens} tokens • {result.time_ms}ms
                      </div>
                    )}
                  </div>
                )
              })}
            </div>
          </motion.div>
        )}
      </div>
    </div>
  )
}

