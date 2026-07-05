import { useMemo, useState } from 'react'

const GROUP_COLORS = {
  Domain: '#3b82f6',
  Structure: '#6366f1',
  Homograph: '#ef4444',
  SSL: '#10b981',
  Keywords: '#f59e0b',
  Path: '#ec4899',
  Other: '#8b5cf6',
}

export default function FeatureContribution({
  topContributors,
  allContributors,
  groupTotals,
  primaryGroup,
  suspiciousCount,
}) {
  const [showAll, setShowAll] = useState(false)
  const [hoveredFeature, setHoveredFeature] = useState('')

  const fullList = useMemo(() => {
    if ((allContributors || []).length > 0) return allContributors || []
    return topContributors || []
  }, [allContributors, topContributors])

  if (!fullList.length) return null

  const displayed = showAll ? fullList : fullList.slice(0, 6)
  const maxContribution = Math.max(...fullList.map((item) => Number(item.local_contribution) || 0), 1)

  return (
    <section className="rounded-2xl border border-[var(--border-paper)] bg-[var(--paper-surface)] p-4 shadow-[var(--shadow-sm)]">
      <p className="mb-2 text-xs uppercase tracking-[0.18em] text-[var(--ink-muted)]">
        FEATURE CONTRIBUTION
      </p>
      <p className="mb-4 text-sm text-[var(--ink-secondary)]">
        {suspiciousCount || 0} of 28 signals contributed meaningfully to this threat score.
      </p>

      {groupTotals && Object.keys(groupTotals).length > 0 && (
        <div className="mb-4 flex flex-wrap gap-2">
          {Object.entries(groupTotals)
            .sort((a, b) => Number(b[1]) - Number(a[1]))
            .filter(([, total]) => Number(total) > 0)
            .map(([group, total]) => {
              const color = GROUP_COLORS[group] || GROUP_COLORS.Other
              const isPrimary = group === primaryGroup
              return (
                <span
                  key={group}
                  className="inline-flex items-center gap-1 rounded-full border px-2 py-1 text-xs"
                  style={{
                    color,
                    borderColor: `${color}55`,
                    background: `${color}16`,
                    fontWeight: isPrimary ? 700 : 500,
                  }}
                >
                  <span
                    className="inline-block h-1.5 w-1.5 rounded-full"
                    style={{ backgroundColor: color }}
                    aria-hidden="true"
                  />
                  {group} ({Number(total).toFixed(0)})
                </span>
              )
            })}
        </div>
      )}

      <div className="space-y-2">
        {displayed.map((feature) => {
          const color = GROUP_COLORS[feature.group] || GROUP_COLORS.Other
          const contribution = Number(feature.local_contribution) || 0
          const width = `${Math.max(2, (contribution / maxContribution) * 100)}%`
          const isHovered = hoveredFeature === feature.feature

          return (
            <div
              key={feature.feature}
              onMouseEnter={() => setHoveredFeature(feature.feature)}
              onMouseLeave={() => setHoveredFeature('')}
              className="rounded-lg p-2 transition"
              style={{ background: isHovered ? 'var(--paper-raised)' : 'transparent' }}
            >
              <div className="mb-1 flex items-center justify-between gap-2">
                <p
                  className="text-sm"
                  style={{
                    color: feature.is_suspicious ? 'var(--ink-primary)' : 'var(--ink-secondary)',
                  }}
                >
                  {feature.label}
                  {feature.is_suspicious && <span className="ml-1 text-[var(--critical)]">●</span>}
                </p>
                <p className="font-mono text-xs text-[var(--ink-muted)]">{contribution.toFixed(1)}</p>
              </div>

              <div className="h-2 overflow-hidden rounded bg-[var(--paper-tinted)]">
                <div
                  className="h-full rounded"
                  style={{
                    width,
                    background: feature.is_suspicious ? color : 'rgba(255,255,255,0.15)',
                    transition: 'width 0.8s cubic-bezier(0.16,1,0.3,1)',
                  }}
                />
              </div>

              {isHovered && feature.why && (
                <p className="mt-1 text-xs italic text-[var(--ink-muted)]">{feature.why}</p>
              )}
            </div>
          )
        })}
      </div>

      {fullList.length > 6 && (
        <button
          type="button"
          onClick={() => setShowAll((prev) => !prev)}
          className="mt-3 text-sm text-[var(--accent)] underline-offset-2 hover:underline"
        >
          {showAll ? 'Show fewer signals' : `Show all ${fullList.length} signals`}
        </button>
      )}
    </section>
  )
}
