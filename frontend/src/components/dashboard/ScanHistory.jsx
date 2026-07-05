import { compactUrl } from '../../utils/threatUtils'
import StatusBadge from '../ui/StatusBadge'

export default function ScanHistory({ scans = [] }) {
  return (
    <section className="rounded-3xl border border-[var(--border-paper)] bg-[var(--paper-surface)] p-5 shadow-[var(--shadow-sm)]">
      <div className="mb-4 flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <p className="font-heading text-xl tracking-[0.1em] text-[var(--ink-primary)]">Scan History</p>
          <p className="text-sm text-[var(--ink-secondary)]">Review the latest scanned URLs and their risk assessment.</p>
        </div>
        <p className="text-sm text-[var(--ink-muted)]">Showing the most recent {scans.length} scans.</p>
      </div>

      {scans.length === 0 ? (
        <div className="rounded-3xl border border-[var(--border-faint)] bg-[var(--paper-raised)] p-5 text-sm text-[var(--ink-secondary)]">
          No scans yet. Run a scan from the landing page to populate your history.
        </div>
      ) : (
        <div className="overflow-x-auto rounded-3xl border border-[var(--border-faint)] bg-[var(--paper-raised)]">
          <table className="w-full min-w-[640px] border-collapse text-left text-sm">
            <thead>
              <tr className="bg-[var(--paper-tinted)] text-[var(--ink-muted)]">
                <th className="px-4 py-3 font-normal uppercase tracking-[0.15em]">Input</th>
                <th className="px-4 py-3 font-normal uppercase tracking-[0.15em]">Score</th>
                <th className="px-4 py-3 font-normal uppercase tracking-[0.15em]">Threat</th>
                <th className="px-4 py-3 font-normal uppercase tracking-[0.15em]">Time</th>
              </tr>
            </thead>
            <tbody>
              {scans.map((scan) => (
                <tr key={scan.scan_id} className="hover:bg-[var(--paper-surface)]">
                  <td className="border-b border-[var(--border-faint)] px-4 py-4 font-mono text-[var(--ink-primary)] ">
                    {compactUrl(scan.input_value, 52)}
                  </td>
                  <td className="border-b border-[var(--border-faint)] px-4 py-4 font-mono text-[var(--ink-primary)]">
                    {scan.threat_score}/100
                  </td>
                  <td className="border-b border-[var(--border-faint)] px-4 py-4">
                    <StatusBadge level={scan.threat_level} score={scan.threat_score} />
                  </td>
                  <td className="border-b border-[var(--border-faint)] px-4 py-4 text-[var(--ink-secondary)]">
                    {new Date(scan.timestamp || Date.now()).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  )
}
