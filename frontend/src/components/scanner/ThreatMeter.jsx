import { motion } from 'framer-motion'
import { useEffect, useMemo, useState } from 'react'
import { getThreatColor, getThreatLabel, normalizeThreatLevel } from '../../utils/threatUtils'

export default function ThreatMeter({ score = 0, level }) {
  const safeScore = Math.max(0, Math.min(100, Number(score) || 0))
  const normalizedLevel = normalizeThreatLevel(level, safeScore)
  const color = getThreatColor(normalizedLevel, safeScore)
  const label = getThreatLabel(normalizedLevel, safeScore)

  const radius = 120
  const arcLength = Math.PI * radius

  const [displayScore, setDisplayScore] = useState(0)

  useEffect(() => {
    let frame = null
    const durationMs = 1500
    const start = performance.now()

    const update = (now) => {
      const elapsed = now - start
      const progress = Math.min(elapsed / durationMs, 1)
      setDisplayScore(Math.round(progress * safeScore))

      if (progress < 1) {
        frame = requestAnimationFrame(update)
      }
    }

    frame = requestAnimationFrame(update)

    return () => {
      if (frame) cancelAnimationFrame(frame)
    }
  }, [safeScore])

  const strokeDashoffset = useMemo(
    () => arcLength - (arcLength * safeScore) / 100,
    [arcLength, safeScore]
  )

  return (
    <div className="relative mx-auto w-full max-w-[360px] rounded-[32px] border border-[var(--border-paper)] bg-[var(--paper-surface)] p-5 shadow-[var(--shadow-md)]">
      <div className="mb-7 flex items-start justify-between">
        <div>
          <p className="text-sm uppercase tracking-[0.18em] text-[var(--ink-muted)]">Risk Gauge</p>
          <p className="text-xl font-semibold text-[var(--ink-primary)]">Threat score</p>
        </div>
        <span className="rounded-full bg-[var(--paper-tinted)] px-3 py-1 text-xs font-semibold uppercase tracking-[0.18em] text-[var(--ink-secondary)]">
          {label}
        </span>
      </div>

      <svg viewBox="0 0 320 190" className="w-full">
        <defs>
          <linearGradient id="gaugeGradient" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="#2d6a4f" />
            <stop offset="50%" stopColor="#d97706" />
            <stop offset="100%" stopColor="#7f1d1d" />
          </linearGradient>
        </defs>
        <path
          d="M 40 160 A 120 120 0 0 1 280 160"
          fill="none"
          stroke="var(--paper-tinted)"
          strokeWidth="16"
          strokeLinecap="round"
        />
        <motion.path
          d="M 40 160 A 120 120 0 0 1 280 160"
          fill="none"
          stroke="url(#gaugeGradient)"
          strokeWidth="16"
          strokeLinecap="round"
          strokeDasharray={arcLength}
          initial={{ strokeDashoffset: arcLength }}
          animate={{ strokeDashoffset }}
          transition={{ duration: 1.5, ease: 'easeOut' }}
        />
      </svg>

      <div className="pointer-events-none absolute inset-x-0 top-[45%] -translate-y-1/2 text-center">
        <p className="font-mono text-5xl font-bold tracking-tight text-[var(--ink-primary)]">{displayScore}</p>
        <p className="mt-1 text-sm uppercase tracking-[0.22em] text-[var(--ink-muted)]">score</p>
      </div>
    </div>
  )
}
