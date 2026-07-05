const API_BASE = 'http://localhost:8000'

const BADGE_PRESET = {
  loading: { text: '...', color: '#777777' },
  unknown: { text: '-', color: '#444444' },
  safe: { text: '✓', color: '#00FF88' },
  suspicious: { text: '?', color: '#FFB800' },
  dangerous: { text: '!', color: '#FF6B35' },
  critical: { text: '!', color: '#FF3B3B' },
}

function isScannableUrl(url) {
  if (!url) return false
  return !/^(chrome|edge|about|devtools|chrome-extension):/i.test(url)
}

function getBadgeForScore(score = 0) {
  if (score >= 80) return BADGE_PRESET.critical
  if (score >= 60) return BADGE_PRESET.dangerous
  if (score >= 40) return BADGE_PRESET.suspicious
  return BADGE_PRESET.safe
}

function setBadge(tabId, preset) {
  chrome.action.setBadgeText({ text: preset.text, tabId })
  chrome.action.setBadgeBackgroundColor({ color: preset.color, tabId })
}

function normalizeScanResult(result, url) {
  return {
    ...result,
    input_value: result?.input_value || url,
    threat_score: Number(result?.threat_score || 0),
    threat_level: String(result?.threat_level || 'unknown').toLowerCase(),
    scanned_at: new Date().toISOString(),
  }
}

function getActiveTab() {
  return new Promise((resolve, reject) => {
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
      if (chrome.runtime.lastError) {
        reject(new Error(chrome.runtime.lastError.message))
        return
      }

      resolve(tabs?.[0] || null)
    })
  })
}

function getTabById(tabId) {
  return new Promise((resolve, reject) => {
    chrome.tabs.get(tabId, (tab) => {
      if (chrome.runtime.lastError || !tab) {
        reject(new Error(chrome.runtime.lastError?.message || 'Tab not found'))
        return
      }
      resolve(tab)
    })
  })
}

function sessionSet(value) {
  return new Promise((resolve) => {
    chrome.storage.session.set(value, () => resolve())
  })
}

function fetchScanResult(url) {
  return fetch(`${API_BASE}/api/scan/url`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ url }),
  }).then(async (response) => {
    if (!response.ok) {
      const errorBody = await response.text()
      throw new Error(errorBody || `Scan request failed with status ${response.status}`)
    }

    return response.json()
  })
}

async function scanCurrentTab(tabId, url, options = {}) {
  const { notifyOnCritical = true } = options

  if (!isScannableUrl(url)) return null

  setBadge(tabId, BADGE_PRESET.loading)
  chrome.action.setTitle({ tabId, title: 'PhantomShield: Scanning...' })

  try {
    const scanData = await fetchScanResult(url)
    const result = normalizeScanResult(scanData, url)
    const badge = getBadgeForScore(result.threat_score)

    setBadge(tabId, badge)
    chrome.action.setTitle({
      tabId,
      title: `PhantomShield: ${result.threat_level.toUpperCase()} (${result.threat_score}/100)`,
    })

    await sessionSet({ [`scan_${tabId}`]: result })

    chrome.tabs.sendMessage(tabId, {
      type: 'PHANTOMSHIELD_SCAN_RESULT',
      result,
    }).catch(() => {})

    if (notifyOnCritical && result.threat_score >= 80) {
      chrome.notifications.create(`critical_${tabId}_${Date.now()}`, {
        type: 'basic',
        iconUrl: 'icons/icon-48.png',
        title: 'PhantomShield Alert',
        message: `Dangerous site detected! Threat score: ${result.threat_score}/100`,
      })
    }

    return result
  } catch (error) {
    setBadge(tabId, BADGE_PRESET.unknown)
    chrome.action.setTitle({ tabId, title: 'PhantomShield: Scan failed' })

    await sessionSet({
      [`scan_${tabId}`]: {
        input_value: url,
        threat_score: 0,
        threat_level: 'unknown',
        is_phishing: false,
        error: error.message,
        scanned_at: new Date().toISOString(),
      },
    })

    return null
  }
}

async function addFalsePositiveReport(payload = {}) {
  return new Promise((resolve) => {
    chrome.storage.local.get(['false_positive_reports'], (stored) => {
      const current = Array.isArray(stored.false_positive_reports)
        ? stored.false_positive_reports
        : []

      current.unshift({
        ...payload,
        reported_at: new Date().toISOString(),
      })

      chrome.storage.local.set(
        { false_positive_reports: current.slice(0, 200) },
        () => resolve()
      )
    })
  })
}

chrome.runtime.onInstalled.addListener(() => {
  chrome.action.setBadgeText({ text: '' })
})

chrome.webNavigation.onCompleted.addListener((details) => {
  if (details.frameId === 0) {
    scanCurrentTab(details.tabId, details.url)
  }
})

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (!message?.type) return undefined

  if (message.type === 'GET_SCAN_RESULT') {
    chrome.storage.session.get([`scan_${message.tabId}`], (result) => {
      sendResponse(result[`scan_${message.tabId}`] || null)
    })
    return true
  }

  if (message.type === 'RESCAN_TAB') {
    ;(async () => {
      try {
        const tab = message.tabId
          ? await getTabById(message.tabId)
          : await getActiveTab()

        if (!tab?.id || !tab.url) {
          throw new Error('No active tab URL available for scanning.')
        }

        const result = await scanCurrentTab(tab.id, message.url || tab.url, {
          notifyOnCritical: true,
        })

        sendResponse({ ok: true, result })
      } catch (error) {
        sendResponse({ ok: false, error: error.message })
      }
    })()

    return true
  }

  if (message.type === 'REPORT_AS_SAFE') {
    addFalsePositiveReport(message.payload)
      .then(() => sendResponse({ ok: true }))
      .catch((error) => sendResponse({ ok: false, error: error.message }))

    return true
  }

  return undefined
})
