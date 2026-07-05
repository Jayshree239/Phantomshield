import {
  LineChart,
  Line,
  ResponsiveContainer,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
} from 'recharts'

export default function ThreatChart({ data = [] }) {
  return (
    <section className="rounded-3xl border border-[var(--border-paper)] bg-[var(--paper-surface)] p-4 shadow-[var(--shadow-sm)]">
      <p className="mb-3 font-heading text-lg tracking-[0.1em] text-[var(--ink-primary)]">Threat Trend (7 Days)</p>

      <div className="h-72 w-full">
        <ResponsiveContainer>
          <LineChart data={data} margin={{ top: 8, right: 12, left: 4, bottom: 0 }}>
            <CartesianGrid stroke="rgba(255,255,255,0.06)" strokeDasharray="3 5" />
            <XAxis dataKey="date" tick={{ fill: 'var(--text-muted)', fontSize: 12 }} axisLine={false} tickLine={false} />
            <YAxis tick={{ fill: 'var(--text-muted)', fontSize: 12 }} axisLine={false} tickLine={false} allowDecimals={false} />
            <Tooltip
              contentStyle={{
                background: 'var(--bg-card)',
                border: '1px solid var(--border)',
                borderRadius: '16px',
                color: 'var(--text-primary)',
              }}
            />
            <Line type="monotone" dataKey="phishing" stroke="var(--danger)" strokeWidth={2.5} dot={{ r: 4, strokeWidth: 0, fill: 'var(--danger)' }} activeDot={{ r: 6 }} />
            <Line type="monotone" dataKey="safe" stroke="var(--success)" strokeWidth={2.5} dot={{ r: 4, strokeWidth: 0, fill: 'var(--success)' }} activeDot={{ r: 6 }} />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </section>
  )
}
