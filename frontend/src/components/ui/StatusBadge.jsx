import { getThreatMeta, normalizeThreatLevel } from '../../utils/threatUtils'

export default function StatusBadge({ level, score = 0, className = '' }) {
  const normalized = normalizeThreatLevel(level, score)
  const meta = getThreatMeta(normalized, score)

  return (
    <span
      className={`inline-flex items-center rounded-full border px-3 py-1 text-xs font-semibold tracking-[0.15em] ${className}`}
      style={{
        color: meta.color,
        background: meta.bg,
        borderColor: meta.border,
      }}
    >
      {meta.label}
    </span>
  )
}
