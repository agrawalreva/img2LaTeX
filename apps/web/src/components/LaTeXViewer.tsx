import { useState } from 'react'
import { Copy, Check, Download, Sparkles } from 'lucide-react'
import { motion } from 'framer-motion'

interface LaTeXViewerProps {
  latex: string
  tokens?: number
  timeMs?: number
  onCopy?: () => void
}

export default function LaTeXViewer({ latex, tokens, timeMs, onCopy }: LaTeXViewerProps) {
  const [copied, setCopied] = useState(false)

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(latex)
      setCopied(true)
      onCopy?.()
      setTimeout(() => setCopied(false), 2000)
    } catch (err) {
      console.error('Failed to copy:', err)
    }
  }

  const handleDownload = () => {
    const blob = new Blob([latex], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'latex_output.tex'
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden"
    >
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-slate-100 bg-slate-50/50">
        <div className="flex items-center space-x-2">
          <div className="w-2 h-2 rounded-full bg-emerald-500" />
          <h3 className="font-medium text-slate-700">Generated LaTeX</h3>
        </div>
        
        <div className="flex items-center space-x-3 text-sm text-slate-500">
          {tokens && (
            <span className="flex items-center">
              <Sparkles size={14} className="mr-1" />
              {tokens} tokens
            </span>
          )}
          {timeMs && (
            <span>{timeMs}ms</span>
          )}
        </div>
      </div>

      {/* LaTeX Content */}
      <div className="p-4">
        <div className="relative">
          <pre className="text-sm font-mono text-slate-800 bg-slate-50 rounded-lg p-4 overflow-x-auto border border-slate-200">
            <code>{latex}</code>
          </pre>
          
          {/* Copy Button */}
          <button
            onClick={handleCopy}
            className="absolute top-2 right-2 p-2 rounded-md bg-white/80 backdrop-blur-sm border border-slate-200 text-slate-600 hover:text-slate-800 hover:bg-white transition-all"
          >
            {copied ? (
              <Check size={16} className="text-emerald-600" />
            ) : (
              <Copy size={16} />
            )}
          </button>
        </div>

        {/* Action Buttons */}
        <div className="flex items-center justify-between mt-4 pt-4 border-t border-slate-100">
          <div className="text-xs text-slate-500">
            {copied && (
              <span className="text-emerald-600 font-medium">
                ✓ Copied to clipboard
              </span>
            )}
          </div>
          
          <div className="flex space-x-2">
            <button
              onClick={handleDownload}
              className="inline-flex items-center px-3 py-1.5 text-sm bg-slate-100 text-slate-700 rounded-md hover:bg-slate-200 transition-colors"
            >
              <Download size={14} className="mr-1.5" />
              Download .tex
            </button>
          </div>
        </div>
      </div>
    </motion.div>
  )
}
