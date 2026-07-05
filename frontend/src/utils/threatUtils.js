const LEVELS = {
  safe: {
    label: 'SAFE',
    color: '#2D6A4F',
    bg: '#D8F3DC',
    border: '#95D5B2',
  },
  suspicious: {
    label: 'SUSPICIOUS',
    color: '#92400E',
    bg: '#FEF3C7',
    border: '#FCD34D',
  },
  dangerous: {
    label: 'DANGEROUS',
    color: '#7C2D12',
    bg: '#FFEDD5',
    border: '#FB923C',
  },
  critical: {
    label: 'CRITICAL',
    color: '#7F1D1D',
    bg: '#FEE2E2',
    border: '#FCA5A5',
  },
}

export function normalizeThreatLevel(level, score = 0) {
  if (typeof level === 'string' && LEVELS[level.toLowerCase()]) {
    return level.toLowerCase()
  }

  if (score >= 80) return 'critical'
  if (score >= 60) return 'dangerous'
  if (score >= 40) return 'suspicious'
  return 'safe'
}

export function getThreatMeta(level, score = 0) {
  const key = normalizeThreatLevel(level, score)
  return LEVELS[key]
}

export function getThreatColor(level, score = 0) {
  return getThreatMeta(level, score).color
}

export function getThreatLabel(level, score = 0) {
  return getThreatMeta(level, score).label
}

export function formatAttackType(value = 'unknown') {
  return value
    .replace(/_/g, ' ')
    .replace(/\b\w/g, (char) => char.toUpperCase())
}

export function toPercent(value = 0, decimals = 0) {
  if (Number.isNaN(Number(value))) return '0%'
  return `${(Number(value) * 100).toFixed(decimals)}%`
}

export function compactUrl(url = '', maxLength = 52) {
  if (!url) return ''
  if (url.length <= maxLength) return url
  return `${url.slice(0, maxLength - 3)}...`
}

export function mapScanToChartPoint(scan) {
  const time = new Date(scan.timestamp || Date.now())
  return {
    date: time.toLocaleDateString(undefined, { weekday: 'short' }),
    phishing: scan.is_phishing ? 1 : 0,
    safe: scan.is_phishing ? 0 : 1,
  }
}
