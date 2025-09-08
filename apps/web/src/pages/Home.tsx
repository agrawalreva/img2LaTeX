import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { AlertCircle, CheckCircle, Image as ImageIcon } from 'lucide-react'
import UploadZone from '../components/UploadZone'
import LaTeXViewer from '../components/LaTeXViewer'
import GenerateButton from '../components/GenerateButton'

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

  // Load sample images on component mount
  useEffect(() => {
    const loadSampleImages = async () => {
      try {
        const response = await fetch('/api/sample-images')
        if (response.ok) {
          const data = await response.json()
          setSampleImages(data.sample_images)
        }
      } catch (err) {
        console.error('Failed to load sample images:', err)
      }
    }
    loadSampleImages()
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

  const handleSampleImageClick = async (sampleImage: SampleImage) => {
    setLoading(true)
    setError(null)
    
    try {
      // For now, just show the expected LaTeX
      // In a real implementation, you would load the actual image and run inference
      const mockResult: InferenceResult = {
        latex: sampleImage.expected_latex,
        tokens: 15,
        time_ms: 800,
        id: Date.now()
      }
      setResult(mockResult)
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
          img2LaTeX AI
        </h1>
        <p className="text-xl text-slate-600">
          Transform mathematical images into LaTeX with AI
        </p>
      </motion.div>

      <div className="space-y-6">
        {/* Sample Images */}
        {sampleImages.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-white rounded-xl border border-slate-200 p-6"
          >
            <h2 className="text-xl font-semibold text-slate-800 mb-4 flex items-center">
              <ImageIcon className="mr-2 h-5 w-5" />
              Try Sample Images
            </h2>
            <p className="text-slate-600 mb-4">
              Click on any sample image below to see how the AI converts mathematical expressions to LaTeX:
            </p>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {sampleImages.map((sample) => (
                <motion.button
                  key={sample.id}
                  onClick={() => handleSampleImageClick(sample)}
                  disabled={loading}
                  className="p-4 border border-slate-200 rounded-lg hover:border-blue-300 hover:bg-blue-50 transition-colors text-left disabled:opacity-50 disabled:cursor-not-allowed"
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                >
                  <div className="flex items-center space-x-3">
                    <div className="w-12 h-12 bg-slate-100 rounded-lg flex items-center justify-center">
                      <ImageIcon className="h-6 w-6 text-slate-500" />
                    </div>
                    <div>
                      <h3 className="font-medium text-slate-800">{sample.name}</h3>
                      <p className="text-sm text-slate-600">{sample.description}</p>
                    </div>
                  </div>
                </motion.button>
              ))}
            </div>
          </motion.div>
        )}

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