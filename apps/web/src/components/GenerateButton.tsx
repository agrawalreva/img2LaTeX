import { Loader2, Sparkles } from 'lucide-react'
import { motion } from 'framer-motion'

interface GenerateButtonProps {
  onClick: () => void
  loading: boolean
  disabled?: boolean
}

export default function GenerateButton({ onClick, loading, disabled }: GenerateButtonProps) {
  return (
    <motion.button
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
      onClick={onClick}
      disabled={loading || disabled}
      className={`
        relative w-full py-3 px-6 rounded-xl font-medium transition-all duration-200
        ${loading || disabled
          ? 'bg-slate-200 text-slate-400 cursor-not-allowed'
          : 'bg-gradient-to-r from-slate-700 to-slate-800 text-white hover:from-slate-600 hover:to-slate-700 shadow-lg hover:shadow-xl'
        }
      `}
    >
      <div className="flex items-center justify-center space-x-2">
        {loading ? (
          <>
            <Loader2 size={18} className="animate-spin" />
            <span>Generating LaTeX...</span>
          </>
        ) : (
          <>
            <Sparkles size={18} />
            <span>Generate LaTeX</span>
          </>
        )}
      </div>
      
      {!loading && !disabled && (
        <motion.div
          className="absolute inset-0 rounded-xl bg-gradient-to-r from-emerald-500/20 to-blue-500/20 opacity-0 hover:opacity-100 transition-opacity"
          initial={false}
        />
      )}
    </motion.button>
  )
}
