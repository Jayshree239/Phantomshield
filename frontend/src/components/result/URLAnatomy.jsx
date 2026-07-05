import { useEffect, useState } from 'react'
import api from '../../services/api'

const STATUS_STYLES = {
  critical: {
    bg: 'rgba(239, 68, 68, 0.15)',
    border: 'rgba(239, 68, 68, 0.35)',
    text: '#f87171',
    dot: '#ef4444',
  },
  suspicious: {
    bg: 'rgba(245, 158, 11, 0.15)',
    border: 'rgba(245, 158, 11, 0.35)',
    text: '#fbbf24',
    dot: '#f59e0b',
  },
  safe: {
    bg: 'rgba(16, 185, 129, 0.15)',
    border: 'rgba(16, 185, 129, 0.35)',
    text: '#34d399',
    dot: '#10b981',
  },
  neutral: {
    bg: 'rgba(255, 255, 255, 0.05)',
    border: 'rgba(255, 255, 255, 0.12)',
    text: '#cbd5e1',
    dot: '#94a3b8',
  },
}

export default function URLAnatomy({ url, featureDict, attackTypes }) {
  const [anatomy, setAnatomy] = useState(null)
  const [loading, setLoading] = useState(false)
  const [expanded, setExpanded] = useState(null)
  const [error, setError] = useState('')

  useEffect(() => {
    if (!url) return

    let active = true
    setLoading(true)
    setError('')

    api
      .post('/api/analysis/anatomy', {
        url,
        feature_dict: featureDict || {},
        attack_types: attackTypes || [],
      })
      .then((response) => {
        if (!active) return
        setAnatomy(response.data?.anatomy || null)
      })
      .catch(() => {
        if (!active) return
        setError('Could not load URL anatomy right now.')
        setAnatomy(null)
      })
      .finally(() => {
        if (!active) return
        setLoading(false)
      })

    return () => {
      active = false
    }
  }, [url, featureDict, attackTypes])

  if (!url) return null

  if (loading) {
    return (
      <section className="rounded-2xl border border-[var(--border-paper)] bg-[var(--paper-surface)] p-4 shadow-[var(--shadow-sm)]">
        <p className="mb-2 text-xs uppercase tracking-[0.18em] text-[var(--ink-muted)]">URL ANATOMY</p>
        <div className="h-14 animate-pulse rounded-lg bg-[var(--paper-tinted)]" />
      </section>
    )
  }

  if (!anatomy) {
    if (error) {
      return (
        <section className="rounded-2xl border border-[var(--border-paper)] bg-[var(--paper-surface)] p-4 shadow-[var(--shadow-sm)]">
          <p className="text-xs uppercase tracking-[0.18em] text-[var(--ink-muted)]">URL ANATOMY</p>
          <p className="mt-2 text-sm text-[var(--ink-secondary)]">{error}</p>
        </section>
      )
    }

    return null
  }

  return (
    <section className="rounded-2xl border border-[var(--border-paper)] bg-[var(--paper-surface)] p-4 shadow-[var(--shadow-sm)]">
      <p className="mb-2 text-xs uppercase tracking-[0.18em] text-[var(--ink-muted)]">URL ANATOMY</p>
      <p className="mb-3 text-sm text-[var(--ink-secondary)]">
        Each component is labeled by risk. Click any segment to view its note.
      </p>

      <div className="mb-3 break-all rounded-lg border border-[var(--border-paper)] bg-[var(--paper-raised)] p-3 font-mono text-sm leading-8 text-[var(--ink-primary)]">
        {(anatomy.components || []).map((component, index) => {
          const style = STATUS_STYLES[component.status] || STATUS_STYLES.neutral
          const isOpen = expanded === index

          return (
            <span key={`${component.text}-${index}`}>
              <span
                onClick={() => setExpanded(isOpen ? null : index)}
                style={{
                  background: style.bg,
                  border: `1px solid ${style.border}`,
                  color: style.text,
                  borderRadius: '4px',
                  padding: '1px 4px',
                  cursor: component.note ? 'pointer' : 'default',
                  marginRight: '1px',
                }}
                title={component.note || ''}
              >
                {component.text}
              </span>

              {isOpen && component.note && (
                <span className="ml-1 inline-flex items-center rounded-md bg-[var(--paper-dark)] px-2 py-1 text-[11px] text-[var(--paper-base)]">
                  <span style={{ color: style.dot, marginRight: '6px' }}>●</span>
                  {component.note}
                </span>
              )}
            </span>
          )
        })}
      </div>

      <div className="flex flex-wrap items-center gap-4">
        {Object.entries(STATUS_STYLES).map(([status, style]) => (
          <div key={status} className="flex items-center gap-2">
            <span
              style={{ background: style.dot }}
              className="inline-block h-2 w-2 rounded-full"
              aria-hidden="true"
            />
            <span className="text-xs capitalize text-[var(--ink-secondary)]">{status}</span>
          </div>
        ))}

        <span className="ml-auto text-xs italic text-[var(--ink-muted)]">{anatomy.summary}</span>
      </div>
    </section>
  )
}
