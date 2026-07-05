import { Lightbulb } from 'lucide-react'

export default function EducationTip({ tip }) {
  if (!tip) return null

  return (
    <section className="rounded-2xl border border-[var(--border-paper)] bg-[var(--paper-surface)] p-4 shadow-[var(--shadow-sm)]">
      <div className="mb-2 flex items-center gap-2 text-[var(--accent)]">
        <Lightbulb size={16} />
        <p className="font-heading text-sm tracking-[0.18em]">PRACTICE TIP</p>
      </div>

      <p className="text-base font-semibold text-[var(--ink-primary)]">{tip.title}</p>
      <p className="mt-2 text-sm text-[var(--ink-secondary)]">{tip.content}</p>

      <div className="mt-3 rounded-lg border border-[var(--border-paper)] bg-[var(--paper-raised)] p-3">
        <p className="text-xs uppercase tracking-[0.15em] text-[var(--ink-muted)]">Example</p>
        <p className="mt-1 text-sm text-[var(--ink-primary)]">{tip.example}</p>
      </div>

      <p className="mt-3 text-xs uppercase tracking-[0.15em] text-[var(--ink-muted)]">
        Difficulty: {tip.difficulty}
      </p>
    </section>
  )
}
