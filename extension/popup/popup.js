import { fallbackTip, getThreatMeta } from '../utils/api.js'

const loadingSteps = [
  'Extracting features...',
  'Running ML model...',
  'Generating explanation...',
]

const state = {
  tabId: null,
  url: '',
  result: null,
  stepTimer: null,
  stepIndex: 0,
}

const elements = {
  currentUrl: document.getElementById('currentUrl'),
  loadingState: document.getElementById('loadingState'),
  resultState: document.getElementById('resultState'),
  loadingStep: document.getElementById('loadingStep'),
  meterRing: document.getElementById('meterRing'),
  scoreValue: document.getElementById('scoreValue'),
  levelValue: document.getElementById('levelValue'),
  statusBadge: document.getElementById('statusBadge'),
  scanTime: document.getElementById('scanTime'),
  explanationSection: document.getElementById('explanationSection'),
  explanationText: document.getElementById('explanationText'),
  tipText: document.getElementById('tipText'),
  toast: document.getElementById('toast'),
  scanManualBtn: document.getElementById('scanManualBtn'),
  viewReportBtn: document.getElementById('viewReportBtn'),
  reportSafeBtn: document.getElementById('reportSafeBtn'),
}

function truncateUrl(url, length = 44) {
  if (!url) return 'No URL detected'
  return url.length <= length ? url : `${url.slice(0, length - 3)}...`
}

function messageRuntime(payload) {
  return new Promise((resolve, reject) => {
    chrome.runtime.sendMessage(payload, (response) => {
      if (chrome.runtime.lastError) {
        reject(new Error(chrome.runtime.lastError.message))
        return
      }
      resolve(response)
    })
  })
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

function startLoadingAnimation() {
  elements.loadingStep.textContent = loadingSteps[0]
  state.stepIndex = 0

  if (state.stepTimer) clearInterval(state.stepTimer)

  state.stepTimer = setInterval(() => {
    state.stepIndex = (state.stepIndex + 1) % loadingSteps.length
    elements.loadingStep.textContent = loadingSteps[state.stepIndex]
  }, 650)
}

function stopLoadingAnimation() {
  if (state.stepTimer) {
    clearInterval(state.stepTimer)
    state.stepTimer = null
  }
}

function setLoading(isLoading) {
  if (isLoading) {
    elements.loadingState.classList.remove('hidden')
    elements.resultState.classList.add('hidden')
    startLoadingAnimation()
    return
  }

  stopLoadingAnimation()
  elements.loadingState.classList.add('hidden')
  elements.resultState.classList.remove('hidden')
}

function showToast(message, isError = false) {
  elements.toast.textContent = message
  elements.toast.style.borderColor = isError
    ? 'rgba(255,59,59,0.6)'
    : 'rgba(0,212,255,0.4)'
  elements.toast.style.background = isError
    ? 'rgba(255,59,59,0.16)'
    : 'rgba(0,212,255,0.14)'
  elements.toast.style.color = isError ? '#FF6B6B' : '#00D4FF'

  elements.toast.classList.remove('hidden')
  setTimeout(() => elements.toast.classList.add('hidden'), 2200)
}

function setThreatMeter(score = 0, level = 'safe') {
  const value = Number(score) || 0
  const normalizedScore = Math.max(0, Math.min(100, value))
  const meta = getThreatMeta(level, normalizedScore)

  elements.meterRing.style.setProperty('--meter-color', meta.color)
  elements.meterRing.style.setProperty('--meter-progress', `${Math.round(normalizedScore * 3.6)}deg`)
  elements.scoreValue.textContent = String(Math.round(normalizedScore))
  elements.levelValue.textContent = meta.label
  elements.statusBadge.textContent = meta.label
  elements.statusBadge.style.color = meta.color
  elements.statusBadge.style.borderColor = `${meta.color}66`
  elements.statusBadge.style.background = `${meta.color}1F`
}

function renderResult(result) {
  state.result = result

  if (!result) {
    setThreatMeter(0, 'safe')
    elements.explanationSection.classList.add('hidden')
    elements.explanationText.textContent = 'No scan result yet. Try scanning manually.'
    elements.tipText.textContent = fallbackTip().content
    elements.scanTime.textContent = 'No scan'
    return
  }

  setThreatMeter(result.threat_score, result.threat_level)

  if (result.threat_score >= 40 && result.explanation?.ai_explanation) {
    elements.explanationSection.classList.remove('hidden')
    elements.explanationText.textContent = result.explanation.ai_explanation
  } else {
    elements.explanationSection.classList.add('hidden')
    elements.explanationText.textContent = 'No phishing explanation required for this page.'
  }

  const tip = result.education_tip || fallbackTip()
  elements.tipText.textContent = tip.content || fallbackTip().content

  const scanTime = result.scanned_at || result.timestamp
  elements.scanTime.textContent = scanTime
    ? new Date(scanTime).toLocaleTimeString()
    : 'just now'
}

async function rescanActiveTab() {
  if (!state.tabId || !state.url) {
    showToast('No scannable tab detected.', true)
    return
  }

  setLoading(true)

  try {
    const response = await messageRuntime({
      type: 'RESCAN_TAB',
      tabId: state.tabId,
      url: state.url,
    })

    if (!response?.ok) {
      throw new Error(response?.error || 'Scan failed')
    }

    renderResult(response.result)
    showToast('Scan updated')
  } catch (error) {
    showToast(error.message, true)
  } finally {
    setLoading(false)
  }
}

async function reportAsSafe() {
  if (!state.result) {
    showToast('No scan result to report.', true)
    return
  }

  try {
    const response = await messageRuntime({
      type: 'REPORT_AS_SAFE',
      payload: {
        tabId: state.tabId,
        url: state.url,
        scanId: state.result.scan_id,
        threatScore: state.result.threat_score,
      },
    })

    if (!response?.ok) {
      throw new Error(response?.error || 'Could not report this page.')
    }

    showToast('Feedback saved')
  } catch (error) {
    showToast(error.message, true)
  }
}

async function initializePopup() {
  setLoading(true)

  try {
    const tab = await getActiveTab()

    if (!tab?.id) {
      throw new Error('Could not find active tab.')
    }

    state.tabId = tab.id
    state.url = tab.url || ''
    elements.currentUrl.textContent = truncateUrl(state.url)

    const cached = await messageRuntime({
      type: 'GET_SCAN_RESULT',
      tabId: state.tabId,
    })

    if (cached && cached.input_value) {
      renderResult(cached)
    } else {
      await rescanActiveTab()
      return
    }
  } catch (error) {
    renderResult(null)
    showToast(error.message, true)
  } finally {
    setLoading(false)
  }
}

function openFullReport() {
  chrome.tabs.create({ url: 'http://localhost:5173/dashboard' })
}

elements.scanManualBtn.addEventListener('click', () => {
  rescanActiveTab()
})

elements.reportSafeBtn.addEventListener('click', () => {
  reportAsSafe()
})

elements.viewReportBtn.addEventListener('click', () => {
  openFullReport()
})

initializePopup()
