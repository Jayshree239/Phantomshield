export const API_BASE = 'http://localhost:8000'

export async function scanUrl(url) {
  const response = await fetch(`${API_BASE}/api/scan/url`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ url }),
  })

  if (!response.ok) {
    const errorText = await response.text()
    throw new Error(errorText || `Scan failed with status ${response.status}`)
  }

  return response.json()
}

export function normalizeThreatLevel(level, score = 0) {
  if (typeof level === 'string') {
    const normalized = level.toLowerCase()
    if (['safe', 'suspicious', 'dangerous', 'critical'].includes(normalized)) {
      return normalized
    }
  }

  if (score >= 80) return 'critical'
  if (score >= 60) return 'dangerous'
  if (score >= 40) return 'suspicious'
  return 'safe'
}

export function getThreatMeta(level, score = 0) {
  const normalized = normalizeThreatLevel(level, score)

  if (normalized === 'critical') {
    return { label: 'CRITICAL', color: '#FF3B3B', badge: '!' }
  }

  if (normalized === 'dangerous') {
    return { label: 'DANGEROUS', color: '#FF6B35', badge: '!' }
  }

  if (normalized === 'suspicious') {
    return { label: 'SUSPICIOUS', color: '#FFB800', badge: '?' }
  }

  return { label: 'SAFE', color: '#00FF88', badge: '✓' }
}

export function fallbackTip() {
  return {
    title: 'Verify before trust',
    content:
      'Do not submit credentials directly on a suspicious page. Open the official website manually and verify account alerts there.',
  }
}
