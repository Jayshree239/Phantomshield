# PhantomShield Detailed Working Document

## 1) Purpose of this document

This document explains the complete working flow of the PhantomShield product in detail, including:
- Full backend and frontend structure
- End-to-end scan lifecycle
- How URL/email/SMS scans are predicted
- Where Gemini is used and what it generates
- How results are rendered in the UI
- How results are saved to Neon and used in dashboard

This is intended as a technical deep-dive reference.

---

## 2) High-level architecture

PhantomShield uses a split architecture:
- Backend: FastAPI service for feature extraction, ML scoring, AI explanation, education tips, and persistence
- Frontend: React app for scanner UI, report UI, dashboard, and education pages
- Database: Neon PostgreSQL for scan history + profile analytics
- AI: Gemini for structured explanation enrichment

Data flow at a glance:
1. User submits URL/email/SMS from frontend
2. Frontend calls backend /api/scan endpoint
3. Backend extracts features and predicts threat via ensemble model
4. Backend classifies attack types
5. For suspicious scans, backend enriches with Gemini explanation bundle
6. Backend generates education tip
7. Backend optionally saves to Neon if user_id is present
8. Frontend renders score, badges, detailed explanation, suspicious elements, and actions

---

## 3) Project file structure

## 3.1 Root structure

```text
phantomshield/
├── backend/
├── frontend/
├── extension/
├── supabase/
├── SPECTER/
└── RUN_PROJECT.md
```

## 3.2 Backend structure (core)

```text
backend/
├── .env
├── .env.example
├── config.py
├── main.py
├── requirements.txt
├── models/
│   ├── db_models.py
│   └── scan_models.py
├── routers/
│   ├── health.py
│   ├── scan.py
│   ├── explain.py
│   ├── education.py
│   └── dashboard.py
├── services/
│   ├── url_scanner.py
│   ├── email_scanner.py
│   ├── sms_scanner.py
│   ├── explainer_service.py
│   ├── education_service.py
│   └── supabase_service.py
├── ml/
│   ├── feature_extractor.py
│   ├── predictor.py
│   ├── ensemble.py
│   ├── model_trainer.py
│   └── models/
│       ├── random_forest.pkl
│       ├── xgboost_model.pkl
│       ├── scaler.pkl
│       └── feature_importance.csv
└── utils/
    ├── domain_utils.py
    ├── ssl_utils.py
    └── rate_limiter.py
```

## 3.3 Frontend structure (core)

```text
frontend/src/
├── App.jsx
├── main.jsx
├── index.css
├── pages/
│   ├── Landing.jsx
│   ├── ScanResult.jsx
│   ├── Dashboard.jsx
│   └── Education.jsx
├── hooks/
│   ├── useScanner.js
│   └── useDashboard.js
├── services/
│   └── api.js
├── components/
│   ├── scanner/
│   │   ├── ScanInput.jsx
│   │   ├── ScanResult.jsx
│   │   ├── ThreatMeter.jsx
│   │   ├── ExplainerCard.jsx
│   │   └── EducationTip.jsx
│   ├── dashboard/
│   │   ├── SecurityScore.jsx
│   │   ├── ThreatChart.jsx
│   │   ├── WeakSpotTracker.jsx
│   │   └── ScanHistory.jsx
│   └── ui/
│       ├── Navbar.jsx
│       ├── StatusBadge.jsx
│       └── LoadingShield.jsx
└── utils/
    └── threatUtils.js
```

---

## 4) Backend detailed flow

## 4.1 App bootstrap and lifecycle

Main file: backend/main.py

Startup behavior:
- FastAPI app starts with CORS + GZip middleware
- During lifespan startup, PhishingPredictor is instantiated once
- Predictor lazily ensures model files exist and are loaded
- API routers are mounted:
  - /api/scan
  - /api/explain
  - /api/education
  - /api/dashboard

Important effect:
- Model loading happens once per process for performance
- Same loaded model objects are reused across requests

## 4.2 Scan endpoints and request entry points

Main scan router: backend/routers/scan.py

Endpoints:
- POST /api/scan/url
- POST /api/scan/email
- POST /api/scan/sms
- POST /api/scan/batch

Primary entry:
- URL path is the full pipeline path
- Email/SMS route through URL flow if a URL is detected

## 4.3 URL scan pipeline (exact sequence)

When POST /api/scan/url is called:

1. Input is validated by URLScanRequest model (backend/models/scan_models.py)
2. scan_url_features() is called (backend/services/url_scanner.py)
3. URLFeatureExtractor.extract() creates:
   - feature_vector (28 numeric features for ML)
   - feature_dict (rich feature metadata)
4. Predictor computes risk:
   - random forest probability
   - xgboost probability
   - weighted ensemble probability
5. threat_score, threat_level, is_phishing, confidence are produced
6. Attack types are classified from feature_dict
7. If threat_score >= 40:
   - Gemini explanation bundle is generated
   - Education tip is generated
8. Response object is assembled with model_versions
9. If user_id exists:
   - result is persisted to Neon
   - user profile is upserted/updated
10. Response returns to frontend

## 4.4 Feature extraction engine (28 features)

File: backend/ml/feature_extractor.py

Feature groups:

1) Domain features (6)
- domain_length
- subdomain_count
- has_ip_address
- tld_suspicious
- domain_contains_brand
- domain_age_score

2) URL structure features (8)
- url_length
- has_at_symbol
- has_double_slash
- special_char_count
- digit_ratio
- hyphen_count
- dot_count
- query_param_count

3) Homograph features (3)
- has_homograph_chars
- homograph_count
- has_unicode

4) SSL features (3)
- has_https
- ssl_valid
- ssl_age_score

5) Keyword features (5)
- has_login_keyword
- has_secure_keyword
- has_verify_keyword
- has_update_keyword
- has_urgency_keyword

6) Path/redirect features (3)
- path_depth
- has_redirect
- subdomain_depth

Additional metadata kept for explanation only:
- _homograph_chars_found
- _domain, _suffix, _subdomain, _scheme

## 4.5 Domain age and WHOIS behavior

Files:
- backend/ml/feature_extractor.py
- backend/utils/domain_utils.py

Behavior:
- Domain age is fetched from WHOIS via get_domain_age_days()
- WHOIS timeout is bounded by WHOIS_TIMEOUT from config/env
- WHOIS noisy logs are suppressed to avoid terminal spam
- If WHOIS fails/timeouts, domain_age_score falls back to neutral 0.5

This keeps scan stable even when WHOIS network calls fail.

## 4.6 ML prediction logic and scoring

Files:
- backend/ml/predictor.py
- backend/ml/ensemble.py

Prediction math:
- X_scaled = scaler.transform(feature_vector)
- rf_proba = RF model probability of phishing class
- xgb_proba = XGBoost probability of phishing class
- ensemble_proba = weighted combination

Weighted formula:
- ensemble = (rf_proba * 0.45 + xgb_proba * 0.55) / (0.45 + 0.55)

Derived outputs:
- threat_score = int(ensemble_proba * 100)
- is_phishing = ensemble_proba > 0.5
- confidence = max(ensemble_proba, 1 - ensemble_proba)
- threat_level thresholds:
  - >= 80: critical
  - >= 60: dangerous
  - >= 40: suspicious
  - else: safe

## 4.7 Attack type classification rules

File: backend/services/url_scanner.py

Mapping examples:
- has_homograph_chars -> HOMOGRAPH
- domain_contains_brand -> BRAND_IMPERSONATION
- has_ip_address -> CREDENTIAL_HARVESTING
- has_urgency_keyword -> URGENCY_MANIPULATION
- ssl invalid + secure keyword -> FAKE_SSL
- very new domain and no prior attack markers -> TYPOSQUATTING
- fallback -> UNKNOWN

This is deterministic rule-based classification layered on top of ML score.

## 4.8 Gemini explanation role (detailed)

File: backend/services/explainer_service.py

Gemini is used only for explanation enrichment, not for primary risk score.

Gemini receives:
- URL
- threat score and level
- detected suspicious indicators from feature_dict

Gemini is instructed to return JSON with fields:
- summary
- attack_technique
- how_attacker_thinks
- ai_explanation
- confidence_rationale
- immediate_actions[]
- safe_alternative
- suspicious_elements[]

Model reliability behavior:
- primary model from env: GEMINI_MODEL
- automatic fallback chain if model fails:
  - gemini-flash-latest
  - gemini-2.5-flash
  - gemini-2.0-flash-lite

Hardening added:
- output JSON extraction/parsing
- attack type + severity normalization
- greeting/self-intro sanitization
- fallback bundle if Gemini output is malformed or unavailable

## 4.9 Education tip generation

File: backend/services/education_service.py

Rules:
- Picks tip by detected attack_types
- Can personalize by user_weak_spots
- Returns structured tip object:
  - title
  - content
  - example
  - category
  - difficulty

## 4.10 Persistence and dashboard aggregation

File: backend/services/supabase_service.py

Note:
- Name kept for compatibility, but implementation is Neon PostgreSQL (psycopg)

Persistence happens only when user_id is present.

Saved in scan_results:
- scan_type
- input_value
- threat_score
- threat_level
- is_phishing
- confidence
- attack_types
- ai_explanation
- scan_time_ms

User profile update:
- total_scans increment
- phishing_caught increment if phishing
- weak_spots updated from attack_types
- security_score recalculated

Dashboard endpoint:
- backend/routers/dashboard.py
- aggregates history, weak spots, trend, profile stats

## 4.11 Email and SMS scan behavior

Files:
- backend/services/email_scanner.py
- backend/services/sms_scanner.py

If URL is found in text:
- route through URL scanner pipeline for full ML + explanation

If URL not found:
- heuristic keyword score is used
- simpler result object returned
- education tip still included

---

## 5) Frontend detailed flow

## 5.1 Routing and pages

File: frontend/src/App.jsx

Routes:
- / -> Landing scanner page
- /result -> Full report page
- /dashboard -> Dashboard analytics page
- /education -> Static education library

## 5.2 User interaction flow (scanner)

Primary files:
- frontend/src/pages/Landing.jsx
- frontend/src/components/scanner/ScanInput.jsx
- frontend/src/hooks/useScanner.js
- frontend/src/services/api.js

Flow:
1. User selects tab: URL, EMAIL, or SMS
2. User submits form
3. ScanInput sends payload with user_id: demo-user
4. useScanner.scan() calls api.js function
5. Axios hits backend endpoint
6. Result stored to:
   - scanResult (latest)
   - recentScans list (last 5)
   - localStorage cache
7. Landing shows ScanResult component
8. VIEW FULL REPORT navigates to /result with full object in route state

## 5.3 Scan result rendering flow

Main files:
- frontend/src/components/scanner/ScanResult.jsx
- frontend/src/components/scanner/ThreatMeter.jsx
- frontend/src/components/scanner/ExplainerCard.jsx
- frontend/src/components/scanner/EducationTip.jsx

Rendered blocks:
- Threat meter arc and score
- Threat status badge
- Input, confidence, phishing yes/no, scan time
- Full AI explanation card for score >= 40
- Practice tip card

## 5.4 Detailed explanation card behavior

File: frontend/src/components/scanner/ExplainerCard.jsx

It displays:
- AI Summary
- Main ai_explanation paragraph
- Attack Technique
- Attacker Mindset
- Why This Score Is Reliable
- Suspicious Elements list
- Immediate Actions checklist
- Safe alternative URL (if available)
- Attack type chips from result.attack_types

COPY REPORT button includes all major explanation fields.

## 5.5 Dashboard behavior

Files:
- frontend/src/pages/Dashboard.jsx
- frontend/src/hooks/useDashboard.js

Behavior:
- Pulls /api/dashboard/{user_id}
- If API unavailable, computes fallback dashboard from local recent scans
- Shows:
  - security score
  - totals
  - phishing caught
  - safe links
  - detection rate
  - trend chart
  - weak spots
  - scan history

---

## 6) Scan result schema (what frontend receives)

Core response model: backend/models/scan_models.py -> ScanResult

Key fields:
- scan_id
- scan_type (url/email/sms)
- input_value
- threat_score
- threat_level
- is_phishing
- confidence
- attack_types[]
- explanation (optional for low-risk scans)
- education_tip
- scan_time_ms
- timestamp
- model_versions

Detailed explanation fields:
- summary
- suspicious_elements[]
- attack_technique
- how_attacker_thinks
- safe_alternative
- ai_explanation
- confidence_rationale
- immediate_actions[]

---

## 7) End-to-end timeline example (URL scan)

Example URL:
- https://paypa1-help-center.xyz/login/confirm

Timeline:
1. Frontend submits URL to /api/scan/url
2. Feature extractor identifies brand-like domain, homograph-like pattern, suspicious TLD, login-style path
3. Predictor computes ensemble probability and maps to dangerous/critical/suspicious/safe
4. Attack types are derived
5. Gemini generates structured explanation bundle
6. Education tip selected from attack profile
7. If user_id provided, scan is written to Neon
8. Frontend renders meter + detailed explanation card + tip

---

## 8) How prediction is made (clear summary)

Prediction is not a single rule and not Gemini-based.

It is a layered system:
1. Feature engineering layer
- 28 engineered URL features extracted

2. ML inference layer
- Random Forest + XGBoost produce phishing probabilities

3. Ensemble layer
- Weighted blend (0.45 RF, 0.55 XGB)

4. Threshold layer
- Score mapped to level via fixed thresholds

5. Rule layer
- Attack-type tags assigned from feature signals

6. Explainability layer
- Gemini produces user-facing narrative and actions

This gives both quantitative scoring and qualitative explanation.

---

## 9) Failure handling and robustness

Backend robustness:
- Missing model files -> auto train and save
- WHOIS timeout/failure -> neutral domain age fallback
- Gemini failure -> structured heuristic fallback explanation
- DB failure -> scan still returns (persistence is non-blocking)

Frontend robustness:
- API errors shown in UI with actionable message
- Latest results and recent scans cached in localStorage
- Dashboard has fallback mode from local scan cache

---

## 10) Gemini role boundaries (important)

Gemini does:
- Explanation quality and depth
- Suspicious-element reasoning language
- Immediate action narrative
- Confidence rationale text

Gemini does not do:
- Primary phishing score calculation
- Threat level thresholding
- Core model probability generation

Those are done by ML + deterministic logic in backend.

---

## 11) Where to extend next (if needed)

Potential improvements:
- Add explanation confidence score derived from JSON quality checks
- Add per-feature contribution chart in frontend
- Persist full explanation bundle fields to DB (currently ai_explanation persisted directly)
- Add runtime telemetry for model fallback frequency
- Add asynchronous queue for external enrichments (WHOIS/VT) to lower latency

---

## 12) Quick reference map

Scan entry:
- backend/routers/scan.py

Feature extraction:
- backend/ml/feature_extractor.py

Prediction:
- backend/ml/predictor.py
- backend/ml/ensemble.py

Explanation (Gemini):
- backend/services/explainer_service.py

Attack tags:
- backend/services/url_scanner.py

Education tips:
- backend/services/education_service.py

Persistence:
- backend/services/supabase_service.py

Frontend scanner flow:
- frontend/src/pages/Landing.jsx
- frontend/src/hooks/useScanner.js
- frontend/src/components/scanner/ScanResult.jsx
- frontend/src/components/scanner/ExplainerCard.jsx

Dashboard:
- backend/routers/dashboard.py
- frontend/src/hooks/useDashboard.js
- frontend/src/pages/Dashboard.jsx
