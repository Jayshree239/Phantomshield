import { BarChart, Bar, Cell, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'

export default function WeakSpotTracker({ items = [] }) {
  const top = items[0]

  return (
    <section className="rounded-3xl border border-[var(--border-paper)] bg-[var(--paper-surface)] p-4 shadow-[var(--shadow-sm)]">
      <p className="mb-3 font-heading text-lg tracking-[0.1em] text-[var(--ink-primary)]">Weak Spot Tracker</p>

      {items.length === 0 ? (
        <p className="text-sm text-[var(--ink-secondary)]">No recurring attack pattern yet. Keep scanning to build your profile.</p>
      ) : (
        <>
          <div className="mb-4 rounded-xl border border-[var(--border-paper)] bg-[var(--paper-raised)] p-3">
            <p className="text-sm text-[var(--ink-secondary)]">
              Most frequent attack pattern:
              <span className="ml-2 font-semibold text-[var(--accent)]">{top.label}</span>
            </p>
            <p className="mt-1 text-xs text-[var(--ink-muted)]">
              You encountered this {top.count} times.
            </p>
          </div>

          <div className="h-64 w-full">
            <ResponsiveContainer>
              <BarChart data={items} layout="vertical" margin={{ left: 8, right: 12 }}>
                <XAxis type="number" allowDecimals={false} hide />
                <YAxis
                  dataKey="label"
                  type="category"
                  tick={{ fill: 'var(--text-muted)', fontSize: 12 }}
                  axisLine={false}
                  tickLine={false}
                  width={140}
                />
                <Tooltip
                  cursor={{ fill: 'rgba(255,255,255,0.04)' }}
                  contentStyle={{
                    background: 'var(--bg-card)',
                    border: '1px solid var(--border)',
                    borderRadius: '16px',
                    color: 'var(--text-primary)',
                  }}
                />
                <Bar dataKey="count" radius={[0, 8, 8, 0]}>
                  {items.map((entry, index) => (
                    <Cell
                      key={`${entry.type}-${index}`}
                      fill={index === 0 ? 'var(--danger)' : 'var(--primary)'}
                    />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </>
      )}
    </section>
  )
}
