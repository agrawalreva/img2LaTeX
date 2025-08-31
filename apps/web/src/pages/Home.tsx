import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { AlertCircle, CheckCircle } from 'lucide-react'
import UploadZone from '../components/UploadZone'
import LaTeXViewer from '../components/LaTeXViewer'
import GenerateButton from '../components/GenerateButton'

interface InferenceResult {
  latex: string
  tokens: number
  time_ms: number
  id: number
}

export default function Home() {
  const [selectedImage, setSelectedImage] = useState<File | null>(null)
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<InferenceResult | null>(null)
  const [error, setError] = useState<string | null>(null)

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
        throw new Error('Failed to generate LaTeX')
      }

      const data = await response.json()
      setResult(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-4xl mx-auto">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center mb-8"
      >
        <h1 className="text-4xl font-bold text-slate-800 mb-4">
          VisionLaTeX Studio
        </h1>
        <p className="text-xl text-slate-600">
          Transform mathematical images into LaTeX with AI
        </p>
      </motion.div>

      <div className="space-y-6">
        {/* Upload Zone */}
        <UploadZone
          onImageSelect={handleImageSelect}
          selectedImage={selectedImage}
          onClearImage={handleClearImage}
        />

        {/* Generate Button */}
        <AnimatePresence>
          {selectedImage && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
            >
              <GenerateButton
                onClick={handleGenerate}
                loading={loading}
                disabled={!selectedImage}
              />
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

        {/* Success Message */}
        <AnimatePresence>
          {result && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="flex items-center p-4 bg-emerald-50 border border-emerald-200 rounded-xl text-emerald-700"
            >
              <CheckCircle size={20} className="mr-3 flex-shrink-0" />
              <span>LaTeX generated successfully!</span>
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
    </div>
  )
}