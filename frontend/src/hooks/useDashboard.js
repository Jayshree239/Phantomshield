import { useCallback, useEffect, useMemo, useState } from 'react'
import { getDashboard } from '../services/api'
import { formatAttackType } from '../utils/threatUtils'

const RECENT_SCANS_KEY = 'phantomshield_recent_scans'

function readRecentScans() {
  try {
    const value = localStorage.getItem(RECENT_SCANS_KEY)
    return value ? JSON.parse(value) : []
  } catch {
    return []
  }
}

function buildFallbackDashboard(scans) {
  const now = new Date()
  const dayMap = new Map()
  const weakSpotCounter = new Map()

  for (let i = 6; i >= 0; i -= 1) {
    const date = new Date(now)
    date.setDate(now.getDate() - i)
    dayMap.set(date.toDateString(), {
      date: date.toLocaleDateString(undefined, { weekday: 'short' }),
      phishing: 0,
      safe: 0,
    })
  }

  scans.forEach((scan) => {
    const key = new Date(scan.timestamp || Date.now()).toDateString()
    if (dayMap.has(key)) {
      const point = dayMap.get(key)
      if (scan.is_phishing) {
        point.phishing += 1
      } else {
        point.safe += 1
      }
      dayMap.set(key, point)
    }

    ;(scan.attack_types || []).forEach((type) => {
      const next = (weakSpotCounter.get(type) || 0) + 1
      weakSpotCounter.set(type, next)
    })
  })

  const totalScans = scans.length
  const phishingCaught = scans.filter((scan) => scan.is_phishing).length
  const safeLinks = totalScans - phishingCaught
  const detectionRate = totalScans > 0 ? Math.round((phishingCaught / totalScans) * 100) : 0
  const securityScore = Math.max(20, Math.min(100, Math.round((safeLinks / Math.max(totalScans, 1)) * 100)))

  const weakSpots = Array.from(weakSpotCounter.entries())
    .map(([type, count]) => ({ type, label: formatAttackType(type), count }))
    .sort((a, b) => b.count - a.count)

  return {
    profile: {
      security_score: securityScore,
      improvement_trend: securityScore >= 60 ? 'improving' : 'stable',
      total_scans: totalScans,
      phishing_caught: phishingCaught,
      safe_links: safeLinks,
      detection_rate: detectionRate,
    },
    history: scans,
    chartData: Array.from(dayMap.values()),
    weakSpots,
  }
}

function normalizeDashboardResponse(data, fallbackScans) {
  if (!data || typeof data !== 'object') {
    return buildFallbackDashboard(fallbackScans)
  }

  const fallback = buildFallbackDashboard(fallbackScans)

  return {
    profile: {
      security_score:
        data.security_score ?? data.profile?.security_score ?? fallback.profile.security_score,
      improvement_trend:
        data.improvement_trend ??
        data.profile?.improvement_trend ??
        fallback.profile.improvement_trend,
      total_scans:
        data.total_scans ?? data.profile?.total_scans ?? fallback.profile.total_scans,
      phishing_caught:
        data.phishing_caught ??
        data.profile?.phishing_caught ??
        fallback.profile.phishing_caught,
      safe_links: data.safe_links ?? data.profile?.safe_links ?? fallback.profile.safe_links,
      detection_rate:
        data.detection_rate ?? data.profile?.detection_rate ?? fallback.profile.detection_rate,
    },
    history: data.history || fallback.history,
    chartData: data.chart_data || data.chartData || fallback.chartData,
    weakSpots: data.weak_spots || data.weakSpots || fallback.weakSpots,
  }
}

export default function useDashboard(userId = 'demo-user') {
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [dashboard, setDashboard] = useState(() =>
    buildFallbackDashboard(readRecentScans())
  )

  const refresh = useCallback(async () => {
    const fallbackScans = readRecentScans()

    setLoading(true)
    setError('')

    try {
      const data = await getDashboard(userId)
      setDashboard(normalizeDashboardResponse(data, fallbackScans))
    } catch (loadError) {
      setDashboard(buildFallbackDashboard(fallbackScans))
      setError(
        loadError.message ||
          'Dashboard API unavailable. Showing local scan history instead.'
      )
    } finally {
      setLoading(false)
    }
  }, [userId])

  useEffect(() => {
    refresh()
  }, [refresh])

  const stats = useMemo(() => {
    const profile = dashboard.profile
    return [
      {
        label: 'Total Scans',
        value: profile.total_scans,
        tone: 'cyan',
      },
      {
        label: 'Phishing Caught',
        value: profile.phishing_caught,
        tone: 'red',
      },
      {
        label: 'Safe Links',
        value: profile.safe_links,
        tone: 'green',
      },
      {
        label: 'Detection Rate',
        value: `${profile.detection_rate}%`,
        tone: 'cyan',
      },
    ]
  }, [dashboard])

  return {
    loading,
    error,
    dashboard,
    stats,
    refresh,
  }
}
