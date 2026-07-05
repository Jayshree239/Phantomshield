import { useEffect, useRef, useState } from 'react'
import api from '../../services/api'

const SUGGESTED_QUESTIONS = [
  'What exactly makes this URL dangerous?',
  'Could this be a false positive?',
  'What would happen if I clicked this link?',
  'How can I verify if this is actually phishing?',
]

export default function ScanQA({
  url,
  threatScore,
  threatLevel,
  attackTypes,
  explanationSummary,
}) {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [started, setStarted] = useState(false)
  const bottomRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])

  const sendQuestion = async (question) => {
    const cleanQuestion = String(question || '').trim()
    if (!cleanQuestion || loading) return

    const userMessage = { role: 'user', content: cleanQuestion }
    const history = [...messages, userMessage]

    setMessages(history)
    setInput('')
    setLoading(true)
    setStarted(true)

    try {
      const response = await api.post('/api/analysis/ask', {
        question: cleanQuestion,
        url,
        threat_score: threatScore,
        threat_level: threatLevel,
        attack_types: attackTypes || [],
        explanation_summary: explanationSummary || '',
        conversation_history: history,
      })

      const answer = response.data?.answer || 'No answer returned for this question.'
      setMessages((prev) => [...prev, { role: 'assistant', content: answer }])
    } catch {
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: 'I could not process that question right now. Please try again.',
        },
      ])
    } finally {
      setLoading(false)
    }
  }

  if (!url) return null

  return (
    <section className="rounded-2xl border border-[var(--border-paper)] bg-[var(--paper-surface)] p-4 shadow-[var(--shadow-sm)]">
      <p className="mb-2 text-xs uppercase tracking-[0.18em] text-[var(--ink-muted)]">
        ASK PHANTOMSHIELD
      </p>
      <p className="mb-4 text-sm text-[var(--ink-secondary)]">
        Ask follow-up questions about this exact scan result.
      </p>

      {!started && (
        <div className="mb-3 flex flex-wrap gap-2">
          {SUGGESTED_QUESTIONS.map((question) => (
            <button
              type="button"
              key={question}
              onClick={() => sendQuestion(question)}
              className="rounded-full border border-[var(--border-paper)] bg-[var(--paper-raised)] px-3 py-1 text-xs text-[var(--ink-secondary)] transition hover:border-[var(--border-warm)] hover:text-[var(--ink-primary)]"
            >
              {question}
            </button>
          ))}
        </div>
      )}

      {messages.length > 0 && (
        <div className="mb-3 flex max-h-[320px] flex-col gap-3 overflow-y-auto rounded-xl border border-[var(--border-paper)] bg-[var(--paper-raised)] p-3">
          {messages.map((msg, index) => (
            <div
              key={`${msg.role}-${index}`}
              className={`max-w-[85%] ${msg.role === 'user' ? 'self-end text-right' : 'self-start text-left'}`}
            >
              <div
                className={`rounded-2xl px-3 py-2 text-sm leading-relaxed ${
                  msg.role === 'user'
                    ? 'rounded-br-md border border-[var(--border-warm)] bg-[var(--accent-dim)] text-[var(--accent)]'
                    : 'rounded-bl-md border border-[var(--border-paper)] bg-[var(--paper-surface)] text-[var(--ink-secondary)]'
                }`}
              >
                {msg.content}
              </div>
              <p className="mt-1 text-[11px] text-[var(--ink-muted)]">
                {msg.role === 'user' ? 'You' : 'PhantomShield'}
              </p>
            </div>
          ))}

          {loading && (
            <div className="self-start rounded-2xl rounded-bl-md border border-[var(--border-paper)] bg-[var(--paper-surface)] px-3 py-2 text-sm text-[var(--ink-secondary)]">
              Thinking...
            </div>
          )}

          <div ref={bottomRef} />
        </div>
      )}

      <div className="flex gap-2">
        <input
          value={input}
          onChange={(event) => setInput(event.target.value)}
          onKeyDown={(event) => {
            if (event.key === 'Enter' && !event.shiftKey) {
              event.preventDefault()
              sendQuestion(input)
            }
          }}
          disabled={loading}
          placeholder="Ask anything about this scan..."
          className="w-full rounded-xl border border-[var(--border-paper)] bg-[var(--paper-raised)] px-3 py-2 text-sm text-[var(--ink-primary)] outline-none transition placeholder:text-[var(--ink-faint)] focus:border-[var(--accent)]"
        />

        <button
          type="button"
          onClick={() => sendQuestion(input)}
          disabled={loading || !input.trim()}
          className="rounded-xl border border-[var(--border-paper)] bg-[var(--paper-dark)] px-4 py-2 text-sm text-[var(--paper-base)] transition hover:bg-[var(--accent-hover)] disabled:cursor-not-allowed disabled:opacity-40"
        >
          Ask
        </button>
      </div>
    </section>
  )
}
