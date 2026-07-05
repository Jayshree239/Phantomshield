# THIS ROUND 2 PROTOTYPE IS THE MINI VERSION OF THE ACTUAL PROTOTYPE AND THE ORIGINAL VERSION IS FAR MOST ROBUST 
# PRODUCT EVER BUILD .. WITH SEPERATE PYTHON BACKEND WITH TRAINED ML MODEL FOR DETECTION AND STATE OF ART FRONTEND WITH LATEST TECH STACK USED AS PER . 

# SPECTER - Round 2 Prototype
## AI-Based Phishing Detection Using Machine Learning Logic

## Project Structure

- detector.py
- app.html
- README.md

## How To Run

### Option 1: Full Stack (API + Frontend)

Requirements: Python 3.8+

1. Install dependencies

```bash
pip install fastapi uvicorn pydantic tldextract
```

2. Start API

```bash
python detector.py
```

3. Open frontend

Open app.html directly in Chrome or Firefox.

API: http://localhost:8000
Docs: http://localhost:8000/docs
Demo: http://localhost:8000/demo

### Option 2: Frontend Only (No Python)

Open app.html directly in browser.

The UI has a built-in client-side demo fallback if API is unavailable.

## All 5 Required Features - Code Map

- Real-time monitoring:
  - scan_history, alert_queue, session_stats
  - GET /stats, GET /history
- Health Index generation:
  - calculate_health_index()
- RUL prediction:
  - calculate_rul()
- Fault classification:
  - classify_attack()
- Alert system:
  - generate_alert(), GET /alerts

## Judge Demo Endpoint

GET /demo runs 5 test URLs through the full pipeline and returns summarized outputs.

## Suggested Test URLs

Phishing-like:
- http://paypa0.com/secure/login?verify=true&urgent=1
- https://amazon-secure-login.tk/verify/account
- http://192.168.1.1/bank/login.php

Likely safe:
- https://www.google.com
- https://github.com/torvalds/linux
- https://stackoverflow.com

## Technical Approach Summary

- Feature extraction: 28 URL-based signals
- Health Index: weighted threat scoring with transparent rules
- RUL: adapted predictive risk window in hours
- Classification: rule-based phishing attack taxonomy
- Alerts: structured alert objects with severity and action recommendation

This prototype is intentionally lightweight and judge-friendly: no npm and no build step.
