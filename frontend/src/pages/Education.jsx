import { AlertTriangle, BookOpenCheck, Clock3, Link2, ShieldCheck } from 'lucide-react'

const libraryTips = [
  {
    id: 'homograph',
    title: 'Look-Alike Character Attacks',
    category: 'Identity Fraud',
    level: 'Intermediate',
    icon: AlertTriangle,
    content:
      'Attackers substitute regular letters with visually similar characters to trick the eye. Verify the domain carefully before clicking on links.',
    example: 'paypal.com vs paypa0.com',
  },
  {
    id: 'urgency',
    title: 'Urgency Manipulation',
    category: 'Social Engineering',
    level: 'Beginner',
    icon: Clock3,
    content:
      'Phishing content often creates a false sense of urgency to force quick decisions. Pause and confirm the request through official channels.',
    example: '"Your account expires today. Click now."',
  },
  {
    id: 'ssl',
    title: 'HTTPS Is Not a Trust Seal',
    category: 'Security Awareness',
    level: 'Intermediate',
    icon: ShieldCheck,
    content:
      'A valid certificate only encrypts traffic and does not prove the site is trustworthy. Always verify the actual domain before entering credentials.',
    example: 'https://fake-brand-login.example can still be malicious',
  },
  {
    id: 'typos',
    title: 'Typosquatting Defense',
    category: 'Domain Hygiene',
    level: 'Beginner',
    icon: Link2,
    content:
      'Attackers register domains with common typos to trap users. Use bookmarks or type the website address manually for critical services.',
    example: 'goggle.com instead of google.com',
  },
]

export default function Education() {
  return (
    <div className="mx-auto w-full max-w-[1200px] px-6 pb-16 pt-10 sm:px-8 lg:px-10">
      <section className="mb-10 rounded-[32px] border border-[var(--border-paper)] bg-[var(--paper-surface)] p-8 shadow-[var(--shadow-md)]">
        <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
          <div className="max-w-3xl">
            <div className="inline-flex items-center gap-3 rounded-full bg-[var(--accent-dim)] px-4 py-2 text-[var(--accent)]">
              <BookOpenCheck size={22} />
              <span className="font-heading text-xl">Security Tips Library</span>
            </div>
            <h1 className="mt-6 text-4xl font-semibold tracking-tight text-[var(--ink-primary)] sm:text-5xl">
              Learn how phishing attacks work
            </h1>
            <p className="mt-4 max-w-2xl text-base leading-7 text-[var(--ink-secondary)]">
              Build stronger security habits with brief, actionable lessons. Each topic includes a clear example and what to look for next time.
            </p>
          </div>

          <div className="rounded-[28px] border border-[var(--border-faint)] bg-[var(--paper-surface)] p-6 text-sm text-[var(--ink-secondary)] shadow-[var(--shadow-sm)]">
            <p className="font-semibold text-[var(--ink-primary)]">Quick learning guide</p>
            <ul className="mt-3 space-y-3">
              <li>• Know suspicious URL patterns</li>
              <li>• Spot urgency and credential requests</li>
              <li>• Treat HTTPS as hygiene, not trust</li>
              <li>• Use bookmarks for trusted services</li>
            </ul>
          </div>
        </div>
      </section>

      <section className="grid gap-6 xl:grid-cols-2">
        {libraryTips.map((tip) => {
          const Icon = tip.icon
          return (
            <article
              key={tip.id}
              className="group overflow-hidden rounded-[28px] border border-[var(--border-paper)] bg-[var(--paper-surface)] p-6 shadow-[var(--shadow-sm)] transition hover:-translate-y-1 hover:shadow-[var(--shadow-lg)]"
            >
              <div className="flex items-center gap-3">
                <span className="flex h-11 w-11 items-center justify-center rounded-2xl bg-[var(--paper-base)] text-[var(--accent)]">
                  <Icon size={20} />
                </span>
                <div>
                  <p className="text-xs uppercase tracking-[0.22em] text-[var(--ink-muted)]">{tip.category}</p>
                  <h2 className="mt-2 text-2xl font-semibold text-[var(--ink-primary)]">{tip.title}</h2>
                </div>
              </div>

              <div className="mt-5 flex flex-wrap items-center gap-3">
                <span className="rounded-full bg-[var(--paper-tinted)] px-3 py-1 text-xs uppercase tracking-[0.15em] text-[var(--ink-secondary)]">
                  {tip.level}
                </span>
              </div>

              <p className="mt-6 text-base leading-7 text-[var(--ink-secondary)]">{tip.content}</p>

              <div className="mt-6 rounded-[24px] border-l-4 border-[var(--accent)] bg-[var(--paper-raised)] p-4 text-sm font-mono text-[var(--ink-primary)] shadow-sm">
                <p className="text-xs uppercase tracking-[0.18em] text-[var(--ink-muted)]">Example</p>
                <p className="mt-2 break-words">{tip.example}</p>
              </div>
            </article>
          )
        })}
      </section>
    </div>
  )
}
