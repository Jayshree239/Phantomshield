import { AlertTriangle, Copy, CheckCircle2 } from 'lucide-react'
import { useMemo, useState } from 'react'
import { formatAttackType } from '../../utils/threatUtils'

function escapeRegExp(value) {
  return value.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
}

function deriveTokens(url, explanation) {
  const tokenSet = new Set()

  ;(explanation?.suspicious_elements || []).forEach((item) => {
    if (!item?.element) return
    const token = String(item.element).trim()
    if (token.length >= 2 && url.includes(token)) {
      tokenSet.add(token)
    }
  })

  if (tokenSet.size === 0) {
    ;['@', 'xn--', 'login', 'verify', 'secure', 'account', 'update', 'confirm'].forEach(
      (keyword) => {
        if (url.toLowerCase().includes(keyword)) {
          tokenSet.add(keyword)
        }
      }
    )
  }

  return [...tokenSet].sort((a, b) => b.length - a.length)
}

function renderHighlightedUrl(url, tokens) {
  if (!tokens.length) {
    return <span>{url}</span>
  }

  const pattern = new RegExp(`(${tokens.map(escapeRegExp).join('|')})`, 'gi')
  return url.split(pattern).map((part, index) => {
    if (tokens.some((token) => token.toLowerCase() === part.toLowerCase())) {
      return (
        <mark
          key={`${part}-${index}`}
          className="rounded bg-transparent px-[1px] text-[var(--danger-red)] underline decoration-[var(--danger-red)] decoration-2"
        >
          {part}
        </mark>
      )
    }
    return <span key={`${part}-${index}`}>{part}</span>
  })
}

export default function ExplainerCard({ result }) {
  const [copied, setCopied] = useState(false)
  const [expanded, setExpanded] = useState(true)

  const explanation = result?.explanation
  const url = result?.input_value || ''

  const suspiciousTokens = useMemo(() => deriveTokens(url, explanation), [url, explanation])

  if (!explanation) return null

  const reportLines = [
    `Threat Score: ${result.threat_score}/100`,
    `Threat Level: ${result.threat_level}`,
    `URL: ${url}`,
  ]

  if (explanation.summary) {
    reportLines.push('', `Summary: ${explanation.summary}`)
  }

  if (explanation.attack_technique) {
    reportLines.push(`Attack Technique: ${explanation.attack_technique}`)
  }

  if (explanation.how_attacker_thinks) {
    reportLines.push(`Attacker Mindset: ${explanation.how_attacker_thinks}`)
  }

  if (explanation.confidence_rationale) {
    reportLines.push(`Confidence Rationale: ${explanation.confidence_rationale}`)
  }

  if ((explanation.immediate_actions || []).length > 0) {
    reportLines.push('Immediate Actions:')
    ;(explanation.immediate_actions || []).forEach((action) => {
      reportLines.push(`- ${action}`)
    })
  }

  reportLines.push('', explanation.ai_explanation || '')
  const reportBody = reportLines.join('\n')

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(reportBody)
      setCopied(true)
      setTimeout(() => setCopied(false), 1200)
    } catch {
      setCopied(false)
    }
  }

  return (
    <section className="rounded-2xl border border-[var(--dangerous-border)] bg-[var(--paper-surface)] p-4 shadow-[var(--shadow-sm)]">
      <div className="mb-3 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex items-center gap-2 text-[var(--dangerous)]">
          <AlertTriangle size={18} />
          <p className="font-heading text-sm tracking-[0.16em]">ATTACK DECODED</p>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          <button
            type="button"
            onClick={() => setExpanded((current) => !current)}
            className="rounded-2xl border border-[var(--border-paper)] bg-[var(--paper-raised)] px-4 py-2 text-xs font-semibold uppercase tracking-[0.14em] text-[var(--ink-secondary)] transition hover:border-[var(--border-warm)] hover:text-[var(--ink-primary)]"
          >
            {expanded ? 'Hide details' : 'Show details'}
          </button>
          <button
            type="button"
            onClick={handleCopy}
            className="inline-flex items-center gap-1 rounded-2xl border border-[var(--border-paper)] bg-[var(--paper-raised)] px-4 py-2 text-xs font-semibold uppercase tracking-[0.14em] text-[var(--ink-secondary)] transition hover:border-[var(--border-warm)] hover:text-[var(--ink-primary)]"
          >
            {copied ? <CheckCircle2 size={14} /> : <Copy size={14} />}
            {copied ? 'Copied' : 'Copy report'}
          </button>
        </div>
      </div>

      <div className="rounded-lg border border-[var(--border-paper)] bg-[var(--paper-raised)] p-4">
        <p className="mb-1 text-xs uppercase tracking-[0.16em] text-[var(--ink-muted)]">Scanned URL</p>
        <p className="break-all font-mono text-sm text-[var(--ink-primary)]">
          {renderHighlightedUrl(url, suspiciousTokens)}
        </p>
      </div>

      <div className="mt-4 rounded-3xl border border-[var(--border-faint)] bg-[var(--paper-surface)] p-4 shadow-[var(--shadow-sm)]">
        <div className="flex flex-col gap-2 md:flex-row md:items-center md:justify-between">
          <div>
            <p className="text-xs uppercase tracking-[0.16em] text-[var(--ink-muted)]">Threat snapshot</p>
            <p className="mt-2 text-lg font-semibold text-[var(--ink-primary)]">Key indicators and next actions</p>
          </div>
          <span className="rounded-full bg-[var(--paper-tinted)] px-3 py-1 text-xs uppercase tracking-[0.16em] text-[var(--ink-secondary)]">
            {result.threat_score}/100
          </span>
        </div>

        {expanded && (
          <div className="mt-4 space-y-4">
            {explanation.summary && (
              <div className="rounded-2xl border border-[var(--border-warm)] bg-[var(--accent-dim)] p-4">
                <p className="text-xs uppercase tracking-[0.15em] text-[var(--accent)]">AI Summary</p>
                <p className="mt-2 text-sm text-[var(--ink-primary)]">{explanation.summary}</p>
              </div>
            )}

            <p className="text-sm text-[var(--ink-secondary)]">{explanation.ai_explanation}</p>

            <div className="grid gap-3 md:grid-cols-2">
              {explanation.attack_technique && (
                <div className="rounded-2xl border border-[var(--border-paper)] bg-[var(--paper-surface)] p-4">
                  <p className="text-xs uppercase tracking-[0.15em] text-[var(--ink-muted)]">Attack Technique</p>
                  <p className="mt-2 text-sm text-[var(--ink-primary)]">{explanation.attack_technique}</p>
                </div>
              )}
              {explanation.how_attacker_thinks && (
                <div className="rounded-2xl border border-[var(--border-paper)] bg-[var(--paper-surface)] p-4">
                  <p className="text-xs uppercase tracking-[0.15em] text-[var(--ink-muted)]">Attacker Mindset</p>
                  <p className="mt-2 text-sm text-[var(--ink-secondary)]">{explanation.how_attacker_thinks}</p>
                </div>
              )}
            </div>

            {explanation.confidence_rationale && (
              <div className="rounded-2xl border border-[var(--border-paper)] bg-[var(--paper-surface)] p-4">
                <p className="text-xs uppercase tracking-[0.15em] text-[var(--ink-muted)]">Why This Score Is Reliable</p>
                <p className="mt-2 text-sm text-[var(--ink-secondary)]">{explanation.confidence_rationale}</p>
              </div>
            )}

            {(result.attack_types || []).length > 0 && (
              <div className="flex flex-wrap gap-2">
                {(result.attack_types || []).map((attack) => (
                  <span
                    key={attack}
                    className="rounded-full border border-[var(--border-paper)] bg-[var(--paper-raised)] px-3 py-1 text-[10px] uppercase tracking-[0.12em] text-[var(--accent)]"
                  >
                    {formatAttackType(attack)}
                  </span>
                ))}
              </div>
            )}

            {(explanation.suspicious_elements || []).length > 0 && (
              <div className="rounded-2xl border border-[var(--border-paper)] bg-[var(--paper-surface)] p-4">
                <p className="text-xs uppercase tracking-[0.15em] text-[var(--ink-muted)]">Suspicious Elements</p>
                <ul className="mt-3 space-y-2">
                  {explanation.suspicious_elements.map((item, index) => (
                    <li key={`${item.element}-${index}`} className="text-sm text-[var(--ink-secondary)]">
                      <span className="mr-2 inline-block h-2 w-2 rounded-full bg-[var(--critical)]" />
                      <span className="font-mono text-[var(--ink-primary)]">{item.element}</span> - {item.reason}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {(explanation.immediate_actions || []).length > 0 && (
              <div className="rounded-2xl border border-[var(--critical-border)] bg-[var(--critical-bg)] p-4">
                <p className="text-xs uppercase tracking-[0.15em] text-[var(--critical)]">Immediate Actions</p>
                <ul className="mt-3 space-y-2">
                  {explanation.immediate_actions.map((action, index) => (
                    <li key={`${action}-${index}`} className="text-sm text-[var(--ink-secondary)]">
                      <span className="mr-2 inline-block h-2 w-2 rounded-full bg-[var(--critical)]" />
                      {action}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {explanation.safe_alternative && (
              <div className="rounded-2xl border border-[var(--safe-border)] bg-[var(--safe-bg)] p-4 text-sm text-[var(--safe)]">
                Legitimate URL: {explanation.safe_alternative}
              </div>
            )}
          </div>
        )}
      </div>
    </section>
  )
}
