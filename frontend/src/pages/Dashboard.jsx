import SecurityScore from '../components/dashboard/SecurityScore'
import ScanHistory from '../components/dashboard/ScanHistory'
import ThreatChart from '../components/dashboard/ThreatChart'
import WeakSpotTracker from '../components/dashboard/WeakSpotTracker'
import useDashboard from '../hooks/useDashboard'

export default function Dashboard() {
  const { loading, error, dashboard, stats, refresh } = useDashboard('demo-user')

  return (
    <div className="mx-auto w-full max-w-[1200px] space-y-10 px-6 pb-16 pt-10 sm:px-8 lg:px-10">
      <section className="rounded-[32px] border border-[var(--border-paper)] bg-[var(--paper-surface)] p-8 shadow-[var(--shadow-md)]">
        <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
          <div>
            <p className="text-sm uppercase tracking-[0.22em] text-[var(--ink-muted)]">Security dashboard</p>
            <h1 className="mt-2 text-3xl font-semibold tracking-tight text-[var(--ink-primary)] sm:text-4xl">
              PhantomShield risk overview
            </h1>
            <p className="mt-3 max-w-2xl text-base leading-7 text-[var(--ink-secondary)]">
              Monitor your phishing scan results, detect patterns, and track where your security awareness is improving.
            </p>
          </div>
          <button
            type="button"
            onClick={refresh}
            disabled={loading}
            className="inline-flex items-center justify-center rounded-2xl bg-[var(--accent)] px-5 py-3 text-sm font-semibold text-white shadow-sm transition hover:bg-[var(--accent-hover)] disabled:cursor-not-allowed disabled:opacity-60"
          >
            {loading ? 'Refreshing...' : 'Refresh dashboard'}
          </button>
        </div>
      </section>

      <div className="grid gap-6 lg:grid-cols-[1.2fr_0.8fr]">
        <div className="space-y-6">
          <SecurityScore
            score={dashboard.profile.security_score}
            trend={dashboard.profile.improvement_trend}
          />

          <section className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            {stats.map((stat) => (
              <article
                key={stat.label}
                className="rounded-[28px] border border-[var(--border-paper)] bg-[var(--paper-surface)] p-5 shadow-[var(--shadow-sm)]"
              >
                <p className="text-xs uppercase tracking-[0.22em] text-[var(--ink-muted)]">{stat.label}</p>
                <p
                  className={[
                    'mt-3 font-mono text-4xl font-semibold',
                    stat.tone === 'red'
                      ? 'text-[var(--critical)]'
                      : stat.tone === 'green'
                        ? 'text-[var(--safe)]'
                        : 'text-[var(--accent)]',
                  ].join(' ')}
                >
                  {stat.value}
                </p>
              </article>
            ))}
          </section>
        </div>

        <div className="space-y-6">
          <ThreatChart data={dashboard.chartData} />
          <WeakSpotTracker items={dashboard.weakSpots} />
        </div>
      </div>

      {error && (
        <div className="rounded-[28px] border border-[var(--suspicious-border)] bg-[var(--suspicious-bg)] p-5 text-sm text-[var(--suspicious)] shadow-[var(--shadow-sm)]">
          {error}
        </div>
      )}

      <ScanHistory scans={dashboard.history} />
    </div>
  )
}
