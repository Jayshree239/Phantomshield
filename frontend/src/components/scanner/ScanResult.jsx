import { Clock3, Target } from 'lucide-react'
import StatusBadge from '../ui/StatusBadge'
import ThreatMeter from './ThreatMeter'
import ExplainerCard from './ExplainerCard'
import EducationTip from './EducationTip'

export default function ScanResult({ result, onViewFullReport }) {
  if (!result) return null

  return (
    <section className="space-y-10 sm:space-y-12 animate-fade-in">
      <div className="grid items-start gap-8 lg:gap-12 xl:gap-16 lg:grid-cols-[420px_1fr]">
        <ThreatMeter score={result.threat_score} level={result.threat_level} />

        <div className="
          rounded-[32px]
          border
          border-white/10
          bg-[#111827]
          p-7
          sm:p-9
          shadow-[0_10px_40px_rgba(0,0,0,0.35)]
        ">
          <div className="
            flex
            flex-wrap
            items-center
            justify-between
            gap-4
            border-b
            border-white/10
            pb-5
          ">
            <p className="font-heading text-xl tracking-[0.1em] text-[var(--ink-primary)]">Scan Result</p>
            <StatusBadge level={result.threat_level} score={result.threat_score} />
          </div>

          <div className="mt-7 space-y-6">
            <div className="
              rounded-2xl
              border
              border-white/10
              bg-[#172033]
              p-5
            ">
              <p className="text-xs uppercase tracking-[0.18em] text-[var(--ink-muted)]">Input</p>
              <p className="mt-1 break-all font-mono text-sm text-[var(--ink-primary)]">{result.input_value}</p>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="rounded-xl border border-[var(--border-paper)] bg-[var(--paper-raised)] p-4">
                <p className="text-xs uppercase tracking-[0.15em] text-[var(--ink-muted)]">Confidence</p>
                <p className="mt-1 font-mono text-lg text-[var(--ink-primary)]">
                  {Math.round((result.confidence || 0) * 100)}%
                </p>
              </div>

              <div className="rounded-xl border border-[var(--border-paper)] bg-[var(--paper-raised)] p-4">
                <p className="text-xs uppercase tracking-[0.15em] text-[var(--ink-muted)]">Phishing</p>
                <p className="mt-1 text-lg text-[var(--ink-primary)]">{result.is_phishing ? 'Yes' : 'No'}</p>
              </div>
            </div>

            <div className="flex flex-wrap items-center gap-6 py-2 text-sm text-[var(--ink-secondary)] border-t border-b border-white/5">
              <p className="inline-flex items-center gap-2">
                <Clock3 size={14} className="text-blue-400" />
                Scan time: <span className="font-mono text-white font-semibold">{result.scan_time_ms} ms</span>
              </p>
              <p className="inline-flex items-center gap-2">
                <Target size={14} className="text-blue-400" />
                Threat Score: <span className="font-mono text-white font-semibold">{result.threat_score}/100</span>
              </p>
            </div>

            <div className="pt-2">
            <button
              type="button"
              onClick={onViewFullReport}
              className="w-full rounded-2xl bg-blue-600 px-5 py-3.5 text-sm font-semibold tracking-wider text-white shadow-lg shadow-blue-500/10 transition-all duration-300 hover:bg-blue-500 hover:shadow-blue-500/30 hover:scale-[1.01] active:scale-[0.99]"
            >
              VIEW FULL REPORT &rarr;
            </button>
            </div>
          </div>
        </div>
      </div>

      {result.threat_score >= 40 && <ExplainerCard result={result} />}
      <EducationTip tip={result.education_tip} />
    </section>
  )
}
