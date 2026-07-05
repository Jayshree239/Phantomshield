import { useState } from 'react'

const tabs = [
  { id: 'url', label: 'URL' },
  { id: 'email', label: 'EMAIL' },
  { id: 'sms', label: 'SMS' },
]

export default function ScanInput({ activeTab, setActiveTab, onSubmit, isScanning }) {
  const [url, setUrl] = useState('')
  const [emailForm, setEmailForm] = useState({ subject: '', sender: '', body: '' })
  const [smsMessage, setSmsMessage] = useState('')
  const [formError, setFormError] = useState('')

  const handleSubmit = (event) => {
    event.preventDefault()
    setFormError('')

    if (activeTab === 'url') {
      if (!url.trim()) {
        setFormError('Please paste a URL before scanning.')
        return
      }
      onSubmit('url', { url: url.trim(), user_id: 'demo-user' })
      return
    }

    if (activeTab === 'email') {
      if (!emailForm.sender.trim() || !emailForm.subject.trim() || !emailForm.body.trim()) {
        setFormError('Sender, subject, and body are required for email scanning.')
        return
      }

      onSubmit('email', {
        sender: emailForm.sender.trim(),
        subject: emailForm.subject.trim(),
        body: emailForm.body.trim(),
        user_id: 'demo-user',
      })
      return
    }

    if (!smsMessage.trim()) {
      setFormError('Please enter an SMS message before scanning.')
      return
    }

    onSubmit('sms', {
      message: smsMessage.trim(),
      user_id: 'demo-user',
    })
  }

  return (
    <form
      className="rounded-3xl border border-[var(--border-paper)] bg-[var(--paper-surface)] p-5 shadow-[var(--shadow-md)] sm:p-6"
      onSubmit={handleSubmit}
    >
      <div className="mb-6 grid grid-cols-3 gap-1.5 rounded-2xl border border-white/5 bg-[#0b1329] p-1.5 shadow-[inset_0_1px_3px_rgba(0,0,0,0.4)]">
        {tabs.map((tab) => {
          const isActive = tab.id === activeTab
          return (
            <button
              key={tab.id}
              type="button"
              className={[
                'rounded-xl px-3 py-2.5 text-xs font-semibold tracking-[0.18em] transition-all duration-300 uppercase cursor-pointer',
                isActive
                  ? 'bg-blue-600 text-white border border-blue-500/30 shadow-[0_0_15px_rgba(37,99,235,0.35)] scale-[1.02]'
                  : 'text-slate-400 hover:text-white hover:bg-white/5 border border-transparent hover:scale-[1.01]',
              ].join(' ')}
              onClick={() => setActiveTab(tab.id)}
            >
              {tab.label}
            </button>
          )
        })}
      </div>

      {activeTab === 'url' && (
        <div className="space-y-3">
          <label className="text-xs uppercase tracking-[0.2em] text-[var(--ink-muted)]">
            URL
          </label>
          <input
            value={url}
            onChange={(event) => setUrl(event.target.value)}
            placeholder="https://example.com/..."
            className="w-full rounded-xl border border-[var(--border-paper)] bg-[var(--paper-raised)] px-4 py-3 font-mono text-sm text-[var(--ink-primary)] outline-none transition placeholder:text-[var(--ink-faint)] focus:border-[var(--accent)]"
          />
        </div>
      )}

      {activeTab === 'email' && (
        <div className="space-y-3">
          <input
            value={emailForm.sender}
            onChange={(event) =>
              setEmailForm((current) => ({ ...current, sender: event.target.value }))
            }
            placeholder="Sender email"
            className="w-full rounded-xl border border-[var(--border-paper)] bg-[var(--paper-raised)] px-4 py-3 font-mono text-sm text-[var(--ink-primary)] outline-none transition placeholder:text-[var(--ink-faint)] focus:border-[var(--accent)]"
          />
          <input
            value={emailForm.subject}
            onChange={(event) =>
              setEmailForm((current) => ({ ...current, subject: event.target.value }))
            }
            placeholder="Email subject"
            className="w-full rounded-xl border border-[var(--border-paper)] bg-[var(--paper-raised)] px-4 py-3 font-mono text-sm text-[var(--ink-primary)] outline-none transition placeholder:text-[var(--ink-faint)] focus:border-[var(--accent)]"
          />
          <textarea
            value={emailForm.body}
            onChange={(event) =>
              setEmailForm((current) => ({ ...current, body: event.target.value }))
            }
            rows={6}
            placeholder="Paste email content..."
            className="w-full rounded-xl border border-[var(--border-paper)] bg-[var(--paper-raised)] px-4 py-3 font-mono text-sm text-[var(--ink-primary)] outline-none transition placeholder:text-[var(--ink-faint)] focus:border-[var(--accent)]"
          />
        </div>
      )}

      {activeTab === 'sms' && (
        <div className="space-y-3">
          <label className="text-xs uppercase tracking-[0.2em] text-[var(--ink-muted)]">
            Message
          </label>
          <textarea
            value={smsMessage}
            onChange={(event) => setSmsMessage(event.target.value)}
            rows={5}
            placeholder="Paste SMS message..."
            className="w-full rounded-xl border border-[var(--border-paper)] bg-[var(--paper-raised)] px-4 py-3 font-mono text-sm text-[var(--ink-primary)] outline-none transition placeholder:text-[var(--ink-faint)] focus:border-[var(--accent)]"
          />
        </div>
      )}

      {formError && <p className="mt-3 text-sm text-[var(--critical)]">{formError}</p>}

      <button
        type="submit"
        disabled={isScanning}
        className="mt-4 w-full rounded-xl bg-[var(--paper-light)] px-4 py-3 font-heading text-lg tracking-[0.08em] text-[var(--ink-muted)] transition hover:bg-[var(--accent-hover)] disabled:cursor-not-allowed disabled:opacity-70"
      >
        {isScanning ? 'ANALYZING...' : 'Analyze ->'}
      </button>

      <p className="mt-3 text-center text-xs text-[var(--ink-muted)]">
        Your data is analyzed locally and never stored without consent.
      </p>
    </form>
  )
}
