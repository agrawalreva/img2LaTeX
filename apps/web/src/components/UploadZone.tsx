import { useState, useCallback } from 'react'
import { Upload, Image, X } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'

interface UploadZoneProps {
  onImageSelect: (file: File) => void
  selectedImage?: File | null
  onClearImage: () => void
  onSampleImageDrop?: (sampleData: any) => void
}

export default function UploadZone({ onImageSelect, selectedImage, onClearImage, onSampleImageDrop }: UploadZoneProps) {
  const [isDragOver, setIsDragOver] = useState(false)

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragOver(true)
  }, [])

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragOver(false)
  }, [])

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragOver(false)
    
    // Check if it's a sample image drop
    const sampleData = e.dataTransfer.getData('application/json')
    if (sampleData) {
      try {
        const sample = JSON.parse(sampleData)
        if (onSampleImageDrop) {
          onSampleImageDrop(sample)
        }
        return
      } catch (err) {
        console.error('Failed to parse sample data:', err)
      }
    }
    
    // Handle regular file drop
    const files = Array.from(e.dataTransfer.files)
    const imageFile = files.find(file => file.type.startsWith('image/'))
    
    if (imageFile) {
      onImageSelect(imageFile)
    }
  }, [onImageSelect, onSampleImageDrop])

  const handleFileSelect = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file && file.type.startsWith('image/')) {
      onImageSelect(file)
    }
  }, [onImageSelect])

  if (selectedImage) {
    return (
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className="relative group"
      >
        <div className="relative rounded-xl overflow-hidden bg-slate-50 border border-slate-200">
          <img
            src={URL.createObjectURL(selectedImage)}
            alt="Selected"
            className="w-full h-64 object-contain"
          />
          <div className="absolute inset-0 bg-gradient-to-t from-slate-900/20 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
          <button
            onClick={onClearImage}
            className="absolute top-3 right-3 p-2 rounded-full bg-white/90 backdrop-blur-sm text-slate-600 hover:text-slate-800 hover:bg-white transition-all shadow-sm"
          >
            <X size={16} />
          </button>
        </div>
      </motion.div>
    )
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="w-full"
    >
      <div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        className={`
          relative border-2 border-dashed rounded-xl p-8 text-center transition-all duration-200
          ${isDragOver 
            ? 'border-emerald-300 bg-emerald-50/50' 
            : 'border-slate-300 hover:border-slate-400 bg-slate-50/30 hover:bg-slate-50/50'
          }
        `}
      >
        <AnimatePresence>
          {isDragOver && (
            <motion.div
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.8 }}
              className="absolute inset-0 bg-emerald-50/80 rounded-xl flex items-center justify-center"
            >
              <div className="text-emerald-600">
                <Upload size={32} className="mx-auto mb-2" />
                <p className="font-medium">Drop image here</p>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        <div className="relative z-10">
          <div className="mx-auto w-16 h-16 rounded-full bg-slate-100 flex items-center justify-center mb-4">
            <Image className="w-8 h-8 text-slate-500" />
          </div>
          
          <h3 className="text-lg font-medium text-slate-700 mb-2">
            Upload an image
          </h3>
          
          <p className="text-slate-500 mb-6 max-w-sm mx-auto">
            Drag and drop an image here, or click to browse
          </p>
          
          <label className="inline-flex items-center px-4 py-2 bg-slate-700 text-white rounded-lg hover:bg-slate-600 transition-colors cursor-pointer">
            <Upload size={16} className="mr-2" />
            Choose File
            <input
              type="file"
              accept="image/*"
              onChange={handleFileSelect}
              className="hidden"
            />
          </label>
        </div>
      </div>
    </motion.div>
  )
}
