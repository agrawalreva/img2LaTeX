import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { AlertCircle, History } from 'lucide-react'
import UploadZone from '../components/UploadZone'
import LaTeXViewer from '../components/LaTeXViewer'

interface InferenceResult {
  latex: string
  tokens: number
  time_ms: number
  id: number
}

interface SampleImage {
  id: string
  name: string
  description: string
  url: string
  expected_latex: string
}

export default function Home() {
  const [selectedImage, setSelectedImage] = useState<File | null>(null)
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<InferenceResult | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [sampleImages, setSampleImages] = useState<SampleImage[]>([])
  const [history, setHistory] = useState<InferenceResult[]>([])
  const [showHistory, setShowHistory] = useState(false)

  // Load sample images and history on component mount
  useEffect(() => {
    const loadData = async () => {
      try {
        // Load sample images
        const sampleResponse = await fetch('/api/sample-images')
        if (sampleResponse.ok) {
          const sampleData = await sampleResponse.json()
          setSampleImages(sampleData.sample_images)
        }
        
        // Load history
        const historyResponse = await fetch('/api/history?limit=10')
        if (historyResponse.ok) {
          const historyData = await historyResponse.json()
          setHistory(historyData)
        }
      } catch (err) {
        console.error('Failed to load data:', err)
      }
    }
    loadData()
  }, [])

  const handleImageSelect = (file: File) => {
    setSelectedImage(file)
    setResult(null)
    setError(null)
  }

  const handleClearImage = () => {
    setSelectedImage(null)
    setResult(null)
    setError(null)
  }

  const handleSampleImageDrop = async (sampleImage: SampleImage) => {
    setLoading(true)
    setError(null)
    
    try {
      // Convert sample image URL to a File object
      const response = await fetch(sampleImage.url)
      const blob = await response.blob()
      const file = new File([blob], `${sampleImage.id}.png`, { type: 'image/png' })
      
      // Set the image and run inference
      setSelectedImage(file)
      
      // Run inference with the sample image
      const formData = new FormData()
      formData.append('image', file)

      const inferResponse = await fetch('/api/infer', {
        method: 'POST',
        body: formData,
      })

      if (!inferResponse.ok) {
        const errorData = await inferResponse.json().catch(() => ({ detail: 'Unknown error' }))
        throw new Error(errorData.detail || 'Failed to generate LaTeX')
      }

      const data = await inferResponse.json()
      setResult(data)
      
      // Refresh history
      const historyResponse = await fetch('/api/history?limit=10')
      if (historyResponse.ok) {
        const historyData = await historyResponse.json()
        setHistory(historyData)
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred')
    } finally {
      setLoading(false)
    }
  }

  const handleGenerate = async () => {
    if (!selectedImage) return

    setLoading(true)
    setError(null)

    try {
      const formData = new FormData()
      formData.append('image', selectedImage)

      const response = await fetch('/api/infer', {
        method: 'POST',
        body: formData,
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }))
        throw new Error(errorData.detail || 'Failed to generate LaTeX')
      }

      const data = await response.json()
      setResult(data)
      
      // Refresh history
      const historyResponse = await fetch('/api/history?limit=10')
      if (historyResponse.ok) {
        const historyData = await historyResponse.json()
        setHistory(historyData)
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Header */}
      <div className="bg-white border-b border-slate-200">
        <div className="max-w-6xl mx-auto px-4 py-4 flex justify-between items-center">
          <h1 className="text-2xl font-bold text-slate-800">img2LaTeX AI</h1>
          <button
            onClick={() => setShowHistory(!showHistory)}
            className="flex items-center px-4 py-2 bg-slate-100 hover:bg-slate-200 rounded-lg transition-colors"
          >
            <History className="h-4 w-4 mr-2" />
            History
          </button>
        </div>
      </div>

      <div className="max-w-6xl mx-auto px-4 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Content */}
          <div className="lg:col-span-2 space-y-6">
            {/* Sample Images */}
            {sampleImages.length > 0 && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="bg-white rounded-xl border border-slate-200 p-6"
              >
                <h2 className="text-lg font-semibold text-slate-800 mb-4">
                  Try Sample Equations
                </h2>
                <p className="text-slate-600 mb-4 text-sm">
                  Drag any equation below into the upload area to convert it to LaTeX:
                </p>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  {sampleImages.map((sample) => (
                    <motion.div
                      key={sample.id}
                      className="border border-slate-200 rounded-lg hover:border-blue-300 hover:bg-blue-50 transition-colors cursor-grab active:cursor-grabbing"
                      draggable
                      onDragStart={(e) => {
                        const dragEvent = e as unknown as React.DragEvent
                        dragEvent.dataTransfer.setData('text/plain', sample.url)
                        dragEvent.dataTransfer.setData('application/json', JSON.stringify(sample))
                      }}
                      whileHover={{ scale: 1.02 }}
                      whileTap={{ scale: 0.98 }}
                    >
                      <div className="p-3">
                        <div className="text-sm font-medium text-slate-800 mb-2">
                          {sample.name}
                        </div>
                        <div className="w-full h-24 bg-slate-100 rounded border-2 border-dashed border-slate-300 flex items-center justify-center mb-2 overflow-hidden">
                          <img 
                            src={sample.url} 
                            alt={sample.name}
                            className="max-w-full max-h-full object-contain"
                          />
                        </div>
                      </div>
                    </motion.div>
                  ))}
                </div>
              </motion.div>
            )}

            {/* Upload Zone */}
            <UploadZone
              onImageSelect={handleImageSelect}
              selectedImage={selectedImage}
              onClearImage={handleClearImage}
              onSampleImageDrop={handleSampleImageDrop}
            />

            {/* Generate Button */}
            <AnimatePresence>
              {selectedImage && !result && (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -20 }}
                  className="text-center"
                >
                  <button
                    onClick={handleGenerate}
                    disabled={loading}
                    className="px-8 py-3 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white rounded-lg font-medium transition-colors"
                  >
                    {loading ? 'Processing...' : 'Generate LaTeX'}
                  </button>
                </motion.div>
              )}
            </AnimatePresence>

            {/* Error Message */}
            <AnimatePresence>
              {error && (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -20 }}
                  className="flex items-center p-4 bg-red-50 border border-red-200 rounded-xl text-red-700"
                >
                  <AlertCircle size={20} className="mr-3 flex-shrink-0" />
                  <span>{error}</span>
                </motion.div>
              )}
            </AnimatePresence>

            {/* LaTeX Result */}
            <AnimatePresence>
              {result && (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -20 }}
                >
                  <LaTeXViewer
                    latex={result.latex}
                    tokens={result.tokens}
                    timeMs={result.time_ms}
                  />
                </motion.div>
              )}
            </AnimatePresence>
          </div>

          {/* History Sidebar */}
          <div className="lg:col-span-1">
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              className="bg-white rounded-xl border border-slate-200 p-6"
            >
              <h3 className="text-lg font-semibold text-slate-800 mb-4 flex items-center">
                <History className="h-5 w-5 mr-2" />
                Recent Conversions
              </h3>
              <div className="space-y-3">
                {history.length === 0 ? (
                  <p className="text-slate-500 text-sm">No conversions yet</p>
                ) : (
                  history.map((item) => (
                    <div
                      key={item.id}
                      className="p-3 bg-slate-50 rounded-lg border border-slate-200 cursor-pointer hover:bg-slate-100 transition-colors"
                      onClick={() => {
                        setResult(item)
                        setSelectedImage(null)
                      }}
                    >
                      <div className="text-sm font-mono text-slate-800 mb-1 truncate">
                        {item.latex}
                      </div>
                      <div className="text-xs text-slate-500">
                        {item.tokens} tokens • {item.time_ms}ms
                      </div>
                    </div>
                  ))
                )}
              </div>
            </motion.div>
          </div>
        </div>
      </div>
    </div>
  )
}