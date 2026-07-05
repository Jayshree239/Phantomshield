# PhantomShield

**PhantomShield: AI-Enabled Phishing Detection and Explanation System**

A complete phishing detection prototype that combines: 
- a Python FastAPI backend,
- a React + Vite frontend,
- a browser extension for real-time link protection,
- machine learning with explainable results,
- and educational guidance to help users learn from phishing risks.

## 🚀 Project Overview

PhantomShield detects suspicious URLs, email content, and SMS messages by analyzing URL structure, domain features, SSL properties, keyword patterns, and threat signals. It uses a hybrid machine learning system (Random Forest + XGBoost) with a feature-based ensemble and explainable output.

The system is designed to help users understand why something is suspicious, not just label it as phishing.

## 🔧 What it does

- Scans URLs for phishing risk
- Analyzes email bodies and SMS text
- Extracts 28 security features from URLs and content
- Uses a weighted ML ensemble to predict phishing likelihood
- Produces a threat score and classification
- Generates user-friendly explanations and educational tips
- Stores scan history and user security metrics when configured
- Includes a browser extension for proactive protection

## 📁 Repository Structure

- `backend/` - FastAPI backend, ML model logic, feature extraction, explainability, and API routes
- `frontend/` - React + Vite application for user scanning and dashboard UI
- `extension/` - Chrome extension code to block or warn on dangerous navigation
- `supabase/` - Database schema for persistence and scan history
- `images/`, `screenshots/` - Visual assets and examples
- `RUN_PROJECT.md` - Detailed run guide for Windows

## 🧠 Key Components

### Backend
- `backend/main.py` - FastAPI application entry point
- `backend/config.py` - Environment and configuration handling
- `backend/ml/feature_extractor.py` - Extracts URL and content features
- `backend/ml/predictor.py` - Loads models and makes predictions
- `backend/ml/ensemble.py` - Weighted ensemble logic
- `backend/services/` - Explanation, education, scanning, database integration and more
- `backend/routers/` - API endpoints for scanning, dashboard, health check, education

### Frontend
- `frontend/src/` - React app source code
- `frontend/src/pages/` - Main pages: Scanner, Dashboard, Education, Landing
- `frontend/src/components/` - UI components for scan results, charts, tips, and history
- `frontend/src/hooks/` - Custom hooks for scan and dashboard state
- `frontend/src/services/api.js` - API client for backend communication

### Browser Extension
- `extension/manifest.json` - Extension configuration
- `extension/background.js` - Background event handling and scanning logic
- `extension/content.js` - Page-level warnings and content injection
- `extension/popup/` - Extension popup UI

## 🧪 Why this project is important

Phishing remains one of the most common and dangerous cyber threats. Traditional methods like blacklists are not enough because attackers constantly create new spoofed domains and deceptive messages. PhantomShield improves protection by:

- Detecting phishing using multiple URL and content signals
- Explaining suspicious behavior clearly to users
- Encouraging safer decision-making with education tips
- Supporting multiple channels: web links, email content, and SMS

## 🛠️ Setup Instructions

### Backend
1. Open a terminal in the project root.
2. Create and activate a Python virtual environment.
3. Install dependencies:
   ```bash
   python -m pip install -r backend/requirements.txt
   ```
4. Configure environment variables in `backend/.env`.
5. Run the backend server:
   ```bash
   python -m uvicorn main:app --app-dir "backend" --reload --env-file "backend/.env" --host 0.0.0.0 --port 8000
   ```

### Frontend
1. Open a second terminal in `frontend/`.
2. Install frontend dependencies:
   ```bash
   npm install
   ```
3. Start the React app:
   ```bash
   npm run dev -- --host
   ```

### Browser Extension
1. Load the `extension/` folder in Chrome or Edge as an unpacked extension.
2. Ensure the backend is running and accessible.
3. Use the extension to automatically scan and warn on suspicious pages.

## 💡 Notes for GitHub

- This repository is ready to showcase as a final-year project.
- Include the `README.md` at the root to explain the project clearly to examiners and collaborators.
- Use the backend and frontend docs for installation and execution details.

## 📞 Contact

If you want to improve the system further, add more advanced explainability, or connect it to a cloud-hosted deployment, this repository is already structured for those enhancements.

---

**PhantomShield** is built to help users detect phishing, understand the danger, and learn safer internet behavior.
