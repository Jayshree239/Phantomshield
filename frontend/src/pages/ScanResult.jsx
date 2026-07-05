import { useLocation, useNavigate } from 'react-router-dom'
import FeatureContribution from '../components/result/FeatureContribution'
import ScanQA from '../components/result/ScanQA'
import ThreatNarrative from '../components/result/ThreatNarrative'
import URLAnatomy from '../components/result/URLAnatomy'
import EducationTip from '../components/scanner/EducationTip'
import ExplainerCard from '../components/scanner/ExplainerCard'
import ThreatMeter from '../components/scanner/ThreatMeter'
import StatusBadge from '../components/ui/StatusBadge'

export default function ScanResultPage() {
  const navigate = useNavigate()
  const location = useLocation()

  const result = location.state?.result
  const isUrlScan = String(result?.scan_type || '').toLowerCase() === 'url'
  const contributorBundle = result?.top_contributors || {}
  const topFeatures = contributorBundle.top_contributors || []

  if (!result) {
    return (
      <div className="mx-auto w-full max-w-[1200px] px-6 pb-10 pt-10 sm:px-8 lg:px-10 text-center">
        <p className="text-lg text-[var(--ink-secondary)]">No scan result selected. Run a scan first.</p>
        <button
          type="button"
          onClick={() => navigate('/')}
          className="mt-4 rounded-2xl border border-[var(--border-paper)] bg-[var(--paper-dark)] px-5 py-3 text-sm font-semibold text-[var(--paper-base)] shadow-sm"
        >
          Back to Scanner
        </button>
      </div>
    )
  }

  return (
    <div className="mx-auto w-full max-w-[1200px] px-6 pb-16 pt-10 sm:px-8 lg:px-10">
      <section className="mb-8 rounded-[32px] border border-[var(--border-paper)] bg-[var(--paper-surface)] p-8 shadow-[var(--shadow-md)]">
        <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
          <div>
            <p className="text-sm uppercase tracking-[0.22em] text-[var(--ink-muted)]">Scan report</p>
            <h1 className="mt-3 text-3xl font-semibold tracking-tight text-[var(--ink-primary)] sm:text-4xl">
              PhantomShield detection summary
            </h1>
            <p className="mt-4 max-w-2xl text-base leading-7 text-[var(--ink-secondary)]">
              Review the risk score, threat insights, and recommended actions for this scanned URL.
            </p>
          </div>
          <div className="flex flex-wrap gap-3">
            <button
              type="button"
              onClick={() => navigate('/')}
              className="rounded-2xl border border-[var(--border-paper)] bg-[var(--paper-surface)] px-4 py-2 text-sm font-medium text-[var(--ink-secondary)] transition hover:border-[var(--border-warm)] hover:text-[var(--ink-primary)]"
            >
              Back to Scanner
            </button>
            <button
              type="button"
              onClick={() => navigate('/dashboard')}
              className="rounded-2xl border border-[var(--border-paper)] bg-[var(--paper-surface)] px-4 py-2 text-sm font-medium text-[var(--ink-secondary)] transition hover:border-[var(--border-warm)] hover:text-[var(--ink-primary)]"
            >
              Open Dashboard
            </button>
          </div>
        </div>
      </section>

      <section className="grid gap-6 sm:gap-8 lg:grid-cols-[0.95fr_1.05fr]">
        <ThreatMeter score={result.threat_score} level={result.threat_level} />

        <div className="space-y-6">
          <div className="rounded-[32px] border border-white/5 bg-[var(--paper-surface)] p-6 sm:p-8 shadow-[var(--shadow-md)]">
            <div className="flex flex-wrap items-center justify-between gap-3 border-b border-white/5 pb-4">
              <div>
                <p className="text-xs uppercase tracking-[0.22em] text-[var(--ink-muted)]">Verdict</p>
                <h2 className="mt-1.5 text-2xl font-semibold text-[var(--ink-primary)]">Threat assessment</h2>
              </div>
              <StatusBadge level={result.threat_level} score={result.threat_score} />
            </div>

            <div className="mt-6 grid gap-5 sm:grid-cols-2">
              <div className="rounded-3xl border border-white/5 bg-[#0b1329]/40 p-5">
                <p className="text-xs uppercase tracking-[0.18em] text-[var(--ink-muted)]">Input</p>
                <p className="mt-3 break-all font-mono text-sm text-[var(--ink-primary)] leading-relaxed">{result.input_value}</p>
              </div>
              <div className="grid gap-5">
                <div className="rounded-3xl border border-white/5 bg-[#0b1329]/40 p-5">
                  <p className="text-xs uppercase tracking-[0.18em] text-[var(--ink-muted)]">Confidence</p>
                  <p className="mt-2 font-mono text-3xl font-semibold text-[var(--ink-primary)]">{Math.round((result.confidence || 0) * 100)}%</p>
                </div>
                <div className="rounded-3xl border border-white/5 bg-[#0b1329]/40 p-5">
                  <p className="text-xs uppercase tracking-[0.18em] text-[var(--ink-muted)]">Phishing</p>
                  <p className="mt-2 text-3xl font-semibold text-[var(--ink-primary)]">{result.is_phishing ? 'Yes' : 'No'}</p>
                </div>
              </div>
            </div>

            <div className="mt-5 grid gap-4 rounded-3xl border border-white/5 bg-[var(--paper-raised)] p-5 text-sm text-[var(--ink-secondary)] sm:grid-cols-2">
              <div>Scan time: <span className="font-mono text-white font-semibold">{result.scan_time_ms} ms</span></div>
              <div>Score: <span className="font-mono text-white font-semibold">{result.threat_score}/100</span></div>
            </div>
          </div>

          {isUrlScan && (
            <URLAnatomy
              url={result.input_value}
              featureDict={result.feature_dict}
              attackTypes={result.attack_types}
            />
          )}
        </div>
      </section>

      <div className="grid gap-6 sm:gap-8 mt-6 sm:mt-8 xl:grid-cols-[1.1fr_0.9fr]">
        <ThreatNarrative
          url={result.input_value}
          threatScore={result.threat_score}
          threatLevel={result.threat_level}
          attackTypes={result.attack_types}
          topFeatures={topFeatures}
          isPhishing={result.is_phishing}
        />

        <div className="space-y-6">
          {topFeatures.length > 0 && (
            <FeatureContribution
              topContributors={contributorBundle.top_contributors || []}
              allContributors={contributorBundle.all_contributions || []}
              groupTotals={contributorBundle.group_totals || {}}
              primaryGroup={contributorBundle.primary_group}
              suspiciousCount={contributorBundle.suspicious_count || 0}
            />
          )}

          {result.threat_score >= 40 && <ExplainerCard result={result} />}
          {isUrlScan && (
            <ScanQA
              url={result.input_value}
              threatScore={result.threat_score}
              threatLevel={result.threat_level}
              attackTypes={result.attack_types}
              explanationSummary={result.explanation?.summary || ''}
            />
          )}
        </div>
      </div>

      <EducationTip tip={result.education_tip} />
    </div>
  )
}
