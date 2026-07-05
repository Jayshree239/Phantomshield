import { useEffect, useMemo, useState } from 'react'
import { scanEmail, scanSms, scanUrl } from '../services/api'

const RECENT_SCANS_KEY = 'phantomshield_recent_scans'
const LAST_SCAN_KEY = 'phantomshield_last_scan'

function readJson(key, fallback) {
  try {
    const value = localStorage.getItem(key)
    return value ? JSON.parse(value) : fallback
  } catch {
    return fallback
  }
}

function buildEducationFallback(scanType) {
  return {
    tip_id: `fallback_${scanType}_${Date.now()}`,
    category: 'general',
    title: 'Pause Before You Click',
    content:
      'If a message asks for urgent action, pause and verify from the official app or website instead of using the link inside the message.',
    example:
      'Type the official website manually in your browser rather than opening unknown links from email or SMS.',
    difficulty: 'beginner',
  }
}

export default function useScanner() {
  const [isScanning, setIsScanning] = useState(false)
  const [scanResult, setScanResult] = useState(null)
  const [recentScans, setRecentScans] = useState(() => readJson(RECENT_SCANS_KEY, []))
  const [error, setError] = useState('')

  useEffect(() => {
    try {
      localStorage.removeItem(LAST_SCAN_KEY)
    } catch (e) {
      // Ignore security/sandboxing errors in some environments
    }
  }, [])

  useEffect(() => {
    try {
      localStorage.setItem(RECENT_SCANS_KEY, JSON.stringify(recentScans))
    } catch (e) {
      // Ignore security/sandboxing errors in some environments
    }
  }, [recentScans])

  const hasResults = useMemo(() => Boolean(scanResult), [scanResult])

  const scan = async (scanType, payload) => {
    setError('')
    setIsScanning(true)

    try {
      let result

      if (scanType === 'url') {
        result = await scanUrl(payload)
      } else if (scanType === 'email') {
        result = await scanEmail(payload)
      } else {
        result = await scanSms(payload)
      }

      if (!result.education_tip) {
        result.education_tip = buildEducationFallback(scanType)
      }

      setScanResult(result)
      setRecentScans((prev) => {
        const filtered = prev.filter((item) => item.input_value !== result.input_value)
        return [result, ...filtered]
      })
      return result
    } catch (scanError) {
      setError(
        scanError.message ||
          'Could not scan right now. Check that the backend API is running on localhost:8000.'
      )
      return null
    } finally {
      setIsScanning(false)
    }
  }

  return {
    isScanning,
    scanResult,
    recentScans,
    error,
    hasResults,
    scan,
    setScanResult,
    clearError: () => setError(''),
  }
}
