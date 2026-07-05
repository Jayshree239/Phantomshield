import { motion } from 'framer-motion'
import { Shield } from 'lucide-react'
import { useEffect, useState } from 'react'

const steps = [
  'Extracting features...',
  'Running ML model...',
  'Generating explanation...',
]

export default function LoadingShield() {
  const [stepIndex, setStepIndex] = useState(0)
  const [progress, setProgress] = useState(0)

  useEffect(() => {
    const messageTimer = setInterval(() => {
      setStepIndex((current) => (current + 1) % steps.length)
    }, 700)

    const progressTimer = setInterval(() => {
      setProgress((current) => (current >= 100 ? 100 : current + 2))
    }, 40)

    return () => {
      clearInterval(messageTimer)
      clearInterval(progressTimer)
    }
  }, [])

  return (
    <div className="rounded-3xl border border-[var(--border-paper)] bg-[var(--paper-surface)] p-6 shadow-[var(--shadow-sm)]">
      <div className="mx-auto flex w-full max-w-md flex-col items-center gap-4 text-center">
        <motion.div
          className="relative"
          animate={{ scale: [1, 1.1, 1], opacity: [0.7, 1, 0.7] }}
          transition={{ repeat: Number.POSITIVE_INFINITY, duration: 1.5 }}
        >
          <div className="absolute inset-0 rounded-full bg-[var(--accent-dim)] blur-xl opacity-70" />
          <div className="relative rounded-full border border-[var(--border-paper)] bg-[var(--paper-raised)] p-5 text-[var(--accent)]">
            <Shield size={36} />
          </div>
        </motion.div>

        <div>
          <p className="font-heading text-2xl uppercase tracking-[0.12em] text-[var(--ink-primary)]">
            Analyzing with AI
          </p>
          <motion.p
            key={steps[stepIndex]}
            initial={{ opacity: 0, y: 4 }}
            animate={{ opacity: 1, y: 0 }}
            className="mt-2 text-sm text-[var(--ink-secondary)]"
          >
            {steps[stepIndex]}
          </motion.p>
        </div>

        <div className="h-2 w-full overflow-hidden rounded-full bg-[var(--paper-tinted)]">
          <motion.div
            className="h-full bg-[var(--accent)]"
            animate={{ width: `${progress}%` }}
            transition={{ ease: 'linear', duration: 0.1 }}
          />
        </div>
      </div>
    </div>
  )
}
