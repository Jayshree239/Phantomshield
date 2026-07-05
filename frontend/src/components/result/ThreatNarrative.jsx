import { useEffect, useState } from 'react'
import api from '../../services/api'

export default function ThreatNarrative({
  url,
  threatScore,
  threatLevel,
  attackTypes,
  topFeatures,
  isPhishing,
}) {
  const [narrative, setNarrative] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    if (!url || !isPhishing) {
      setNarrative(null)
      setLoading(false)
      setError('')
      return
    }

    let active = true
    setLoading(true)
    setError('')

    api
      .post('/api/analysis/narrative', {
        url,
        threat_score: threatScore,
        threat_level: threatLevel,
        attack_types: attackTypes || [],
        top_features: topFeatures || [],
        is_phishing: isPhishing,
      })
      .then((response) => {
        if (!active) return
        setNarrative(response.data?.narrative || null)
      })
      .catch(() => {
        if (!active) return
        setError('Threat narrative is unavailable for this scan.')
        setNarrative(null)
      })
      .finally(() => {
        if (!active) return
        setLoading(false)
      })

    return () => {
      active = false
    }
  }, [url, threatScore, threatLevel, attackTypes, topFeatures, isPhishing])

  if (!isPhishing) return null

  if (loading) {
    return (
      <section className="rounded-2xl border border-[var(--border-paper)] bg-[var(--paper-surface)] p-4 shadow-[var(--shadow-sm)]">
        <p className="mb-2 text-xs uppercase tracking-[0.18em] text-[var(--ink-muted)]">THREAT NARRATIVE</p>
        <div className="space-y-2">
          <div className="h-4 w-full animate-pulse rounded bg-[var(--paper-tinted)]" />
          <div className="h-4 w-[82%] animate-pulse rounded bg-[var(--paper-tinted)]" />
          <div className="h-4 w-[70%] animate-pulse rounded bg-[var(--paper-tinted)]" />
        </div>
      </section>
    )
  }

  if (!narrative) {
    if (error) {
      return (
        <section className="rounded-2xl border border-[var(--border-paper)] bg-[var(--paper-surface)] p-4 shadow-[var(--shadow-sm)]">
          <p className="text-xs uppercase tracking-[0.18em] text-[var(--ink-muted)]">THREAT NARRATIVE</p>
          <p className="mt-2 text-sm text-[var(--ink-secondary)]">{error}</p>
        </section>
      )
    }

    return null
  }

  const detailBlocks = [
    { label: 'Who Runs This Attack', value: narrative.attacker_profile },
    { label: 'Who Is Targeted', value: narrative.victim_profile },
    { label: 'Why This Score', value: narrative.severity_justification },
    { label: 'Industry Context', value: narrative.industry_context },
  ].filter((item) => item.value)

  return (
    <section className="rounded-2xl border border-[var(--border-paper)] bg-[var(--paper-surface)] p-4 shadow-[var(--shadow-sm)]">
      <p className="mb-2 text-xs uppercase tracking-[0.18em] text-[var(--ink-muted)]">THREAT NARRATIVE</p>

      {narrative.one_liner && (
        <div className="mb-4 rounded-lg border border-[var(--suspicious-border)] bg-[var(--suspicious-bg)] p-3 text-sm italic text-[var(--suspicious)]">
          "{narrative.one_liner}"
        </div>
      )}

      {(narrative.red_flags_plain || []).length > 0 && (
        <div className="mb-4">
          <p className="mb-2 text-xs uppercase tracking-[0.16em] text-[var(--ink-muted)]">Red Flags</p>
          <div className="space-y-2">
            {(narrative.red_flags_plain || []).map((flag, index) => (
              <p key={`${flag}-${index}`} className="text-sm text-[var(--ink-secondary)]">
                <span className="mr-2 text-[var(--critical)]">⚠</span>
                {flag}
              </p>
            ))}
          </div>
        </div>
      )}

      {detailBlocks.length > 0 && (
        <div className="grid gap-3 md:grid-cols-2">
          {detailBlocks.map((item) => (
            <div key={item.label} className="rounded-lg border border-[var(--border-paper)] bg-[var(--paper-raised)] p-3">
              <p className="text-xs uppercase tracking-[0.14em] text-[var(--ink-muted)]">{item.label}</p>
              <p className="mt-1 text-sm text-[var(--ink-secondary)]">{item.value}</p>
            </div>
          ))}
        </div>
      )}
    </section>
  )
}
