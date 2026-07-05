import { TrendingUp, Shield } from 'lucide-react'
import { motion } from 'framer-motion'

export default function SecurityScore({ score = 0, trend = 'stable' }) {
  const safeScore = Math.max(0, Math.min(100, score))
  const trendText = trend === 'improving' ? '+5 this week' : trend === 'declining' ? '-3 this week' : 'No change'
  const gaugeOffset = 282.6 - (282.6 * safeScore) / 100

  return (
    <section className="rounded-[32px] border border-[var(--border-paper)] bg-[var(--paper-surface)] p-6 shadow-[var(--shadow-md)]">
      <div className="grid gap-6 lg:grid-cols-[0.9fr_0.8fr] lg:items-center">
        <div>
          <p className="font-heading text-xl tracking-[0.1em] text-[var(--ink-primary)]">Security Score</p>
          <p className="mt-3 max-w-xl text-base leading-7 text-[var(--ink-secondary)]">
            Your current phishing awareness score summarises how prepared you are to detect risky links and messages.
          </p>
          <div className="mt-5 inline-flex items-center gap-2 rounded-full border border-[var(--border-paper)] bg-[var(--paper-tinted)] px-4 py-2 text-sm text-[var(--ink-secondary)]">
            <TrendingUp size={16} />
            {trendText}
          </div>
        </div>

        <div className="relative mx-auto flex h-48 w-48 items-center justify-center rounded-full bg-[var(--paper-base)] shadow-[inset_0_0_0_1px_rgba(36,31,25,0.06)]">
          <svg viewBox="0 0 220 220" className="h-full w-full">
            <defs>
              <linearGradient id="scoreGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                <stop offset="0%" stopColor="#2d6a4f" />
                <stop offset="50%" stopColor="#d97706" />
                <stop offset="100%" stopColor="#7f1d1d" />
              </linearGradient>
            </defs>
            <circle
              cx="110"
              cy="110"
              r="45"
              stroke="var(--paper-tinted)"
              strokeWidth="20"
              fill="none"
            />
            <motion.circle
              cx="110"
              cy="110"
              r="45"
              stroke="url(#scoreGradient)"
              strokeWidth="20"
              strokeLinecap="round"
              fill="none"
              strokeDasharray="282.6"
              initial={{ strokeDashoffset: 282.6 }}
              animate={{ strokeDashoffset: gaugeOffset }}
              transition={{ duration: 1.2, ease: 'easeOut' }}
              transform="rotate(-90 110 110)"
            />
          </svg>
          <div className="absolute inset-0 flex flex-col items-center justify-center text-center">
            <Shield size={22} className="text-[var(--accent)]" />
            <p className="mt-2 text-4xl font-bold text-[var(--ink-primary)]">{safeScore}</p>
            <p className="text-xs uppercase tracking-[0.24em] text-[var(--ink-muted)]">score</p>
          </div>
        </div>
      </div>
    </section>
  )
}
