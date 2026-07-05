const BANNER_ID = 'phantomshield-warning-banner'
let latestResult = null

function hasSensitiveInputs() {
  return Boolean(
    document.querySelector(
      [
        'input[type="password"]',
        'input[name*="card" i]',
        'input[name*="otp" i]',
        'input[name*="cvv" i]',
        'input[name*="pin" i]',
      ].join(',')
    )
  )
}

function removeWarningBanner() {
  const banner = document.getElementById(BANNER_ID)
  if (banner) banner.remove()
}

function createWarningBanner() {
  const banner = document.createElement('div')
  banner.id = BANNER_ID
  banner.style.position = 'fixed'
  banner.style.right = '14px'
  banner.style.top = '14px'
  banner.style.zIndex = '2147483647'
  banner.style.maxWidth = '320px'
  banner.style.border = '1px solid rgba(255, 59, 59, 0.5)'
  banner.style.background = 'rgba(15, 15, 15, 0.95)'
  banner.style.color = '#fff'
  banner.style.borderRadius = '12px'
  banner.style.padding = '12px'
  banner.style.fontFamily = "'DM Sans', Arial, sans-serif"
  banner.style.boxShadow = '0 10px 28px rgba(0, 0, 0, 0.45)'

  banner.innerHTML = `
    <div style="display:flex; align-items:center; justify-content:space-between; gap:8px; margin-bottom:8px;">
      <strong style="font-size:13px; color:#FF3B3B; letter-spacing:0.08em;">PHANTOMSHIELD ALERT</strong>
      <button id="${BANNER_ID}-close" style="background:transparent; border:none; color:#bbb; cursor:pointer; font-size:12px;">Dismiss</button>
    </div>
    <p id="${BANNER_ID}-text" style="margin:0; font-size:12px; line-height:1.5; color:rgba(255,255,255,0.9);"></p>
  `

  const closeButton = banner.querySelector(`#${BANNER_ID}-close`)
  closeButton?.addEventListener('click', () => banner.remove())

  return banner
}

function upsertWarningBanner() {
  if (!latestResult || latestResult.threat_score < 60 || !hasSensitiveInputs()) {
    removeWarningBanner()
    return
  }

  let banner = document.getElementById(BANNER_ID)
  if (!banner) {
    banner = createWarningBanner()
    document.documentElement.appendChild(banner)
  }

  const text = banner.querySelector(`#${BANNER_ID}-text`)
  if (text) {
    text.textContent = `This page scored ${latestResult.threat_score}/100 (${String(
      latestResult.threat_level || 'dangerous'
    ).toUpperCase()}). Avoid entering passwords, OTP, or payment details.`
  }
}

const domObserver = new MutationObserver(() => {
  if (latestResult?.threat_score >= 60) {
    upsertWarningBanner()
  }
})

domObserver.observe(document.documentElement, {
  childList: true,
  subtree: true,
})

chrome.runtime.onMessage.addListener((message) => {
  if (message?.type === 'PHANTOMSHIELD_SCAN_RESULT') {
    latestResult = message.result
    upsertWarningBanner()
  }
})

window.addEventListener('beforeunload', () => {
  domObserver.disconnect()
})
