import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { AlertCircle, ShieldCheck, ShieldAlert, ShieldQuestion } from 'lucide-react'
import ScanInput from '../components/scanner/ScanInput'
import ScanResult from '../components/scanner/ScanResult'
import LoadingShield from '../components/ui/LoadingShield'
import StatusBadge from '../components/ui/StatusBadge'
import useScanner from '../hooks/useScanner'
import { compactUrl } from '../utils/threatUtils'

function ResultIcon({ score }) {
  if (score >= 80) return <ShieldAlert size={16} className="text-[var(--danger-red)]" />
  if (score >= 40) return <ShieldQuestion size={16} className="text-[var(--warning)]" />
  return <ShieldCheck size={16} className="text-[var(--safe-green)]" />
}

export default function Landing() {
  const navigate = useNavigate()
  const [activeTab, setActiveTab] = useState('url')
  const { isScanning, scanResult, recentScans, error, scan } = useScanner()

  const handleScan = async (scanType, payload) => {
    await scan(scanType, payload)
  }

  const openFullReport = (result = scanResult) => {
    if (!result) return
    navigate('/result', { state: { result } })
  }

  return (
    <div className="mx-auto w-full max-w-[1200px] px-6 pb-12 pt-10 sm:px-8 lg:px-10">
      <section className="mx-auto mb-8 max-w-4xl text-center">
        <p className="section-label">Security Analysis Tool</p>
        <h1 className="hero-title text-[clamp(2.5rem,6vw,4.5rem)] leading-[1.05] text-[var(--text-primary)]">
          Is this URL safe?
        </h1>
        <p className="mx-auto mt-4 max-w-2xl text-lg leading-8 font-light text-[var(--ink-secondary)]">
          Paste any URL, email, or message. PhantomShield analyzes it against 28 security signals and explains exactly what it finds.
        </p>
      </section>

      <section className="mx-auto w-full max-w-[640px] space-y-4">
        <ScanInput
          activeTab={activeTab}
          setActiveTab={setActiveTab}
          isScanning={isScanning}
          onSubmit={handleScan}
        />

        {error && (
          <div className="flex items-start gap-2 rounded-xl border border-[var(--critical-border)] bg-[var(--critical-bg)] p-3 text-sm text-[var(--critical)]">
            <AlertCircle size={16} className="mt-[2px] shrink-0" />
            <p>{error}</p>
          </div>
        )}

        {isScanning && <LoadingShield />}

        {!isScanning && scanResult && (
          <ScanResult result={scanResult} onViewFullReport={() => openFullReport(scanResult)} />
        )}
      </section>

      <section className="mx-auto mt-10 w-full max-w-4xl rounded-3xl border border-white/5 bg-[#1e293b]/70 p-6 shadow-xl backdrop-blur-md">
        <div className="mb-4 flex items-center justify-between border-b border-white/5 pb-3">
          <div>
            <h3 className="text-lg font-semibold tracking-wide text-white">Recent Security Scans</h3>
            <p className="text-xs text-slate-400 mt-0.5">Real-time threat log of scanned inputs</p>
          </div>
          <span className="rounded-full bg-blue-500/10 border border-blue-500/20 px-3 py-1 text-xs font-semibold text-blue-400">
            {recentScans.length} Scans
          </span>
        </div>

        {recentScans.length === 0 ? (
          <div className="rounded-2xl border border-white/5 bg-slate-900/40 p-6 text-center text-sm text-slate-400">
            No scans performed in this session. Paste a link above to begin.
          </div>
        ) : (
          <div className="max-h-[320px] overflow-y-auto pr-1">
            <ul className="space-y-2">
              {recentScans.map((scan) => (
                <li
                  key={scan.scan_id}
                  className="flex flex-wrap items-center justify-between gap-4 rounded-2xl border border-white/5 bg-slate-900/50 p-4 transition-all duration-300 hover:bg-slate-900/85 hover:translate-x-1"
                >
                  <button
                    type="button"
                    onClick={() => openFullReport(scan)}
                    className="flex min-w-0 flex-1 items-center gap-3 text-left cursor-pointer"
                  >
                    <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-xl bg-slate-800/80 border border-white/5 text-slate-400">
                      <ResultIcon score={scan.threat_score} />
                    </span>
                    <div className="min-w-0">
                      <span className="block truncate font-mono text-sm font-medium text-slate-100 hover:text-blue-400 transition-colors">
                        {compactUrl(scan.input_value, 52)}
                      </span>
                      <span className="block text-[11px] text-slate-400 uppercase tracking-wider mt-0.5">
                        {scan.scan_type || 'URL'} Scan
                      </span>
                    </div>
                  </button>

                  <div className="flex items-center gap-3">
                    <StatusBadge level={scan.threat_level} score={scan.threat_score} />
                    <span className="font-mono text-xs text-slate-400">
                      {new Date(scan.timestamp || Date.now()).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </span>
                    <button
                      type="button"
                      onClick={() => openFullReport(scan)}
                      className="text-xs font-semibold text-blue-400 hover:text-blue-300 tracking-wider uppercase transition-colors cursor-pointer"
                    >
                      Report &rarr;
                    </button>
                  </div>
                </li>
              ))}
            </ul>
          </div>
        )}
      </section>

      <section className="mx-auto mt-10 w-full max-w-4xl">
        <div className="grid gap-6 text-center md:grid-cols-3 md:gap-0">
          {[
            { value: '28', label: 'signals analyzed' },
            { value: 'ML + AI', label: 'powered pipeline' },
            { value: 'Seconds', label: 'to result' },
          ].map((item, index) => (
            <div
              key={item.label}
              className={[
                'px-4',
                index > 0 ? 'md:border-l md:border-[var(--border-paper)]' : '',
              ].join(' ')}
            >
              <p className="font-mono text-2xl text-[var(--ink-primary)]">{item.value}</p>
              <p className="text-sm text-[var(--ink-muted)]">{item.label}</p>
            </div>
          ))}
        </div>
      </section>
    </div>
  )
}
