# PhantomShield: Project Presentation & Viva Preparation Guide

This guide is designed to help every group member thoroughly understand **PhantomShield: AI-Enabled Phishing Detection and Explanation System**, explain it confidently to examiners, and answer potential viva questions.

---

## 1. Project Metadata & Team Details
*   **Project Title:** PhantomShield: AI-Enabled Phishing Detection and Explanation System
*   **University Affiliation:** Savitribai Phule Pune University
*   **College:** Sir Visvesvaraya Institute of Technology (SVIT), Nashik
*   **Department:** Department of Information Technology
*   **Academic Year:** 2025–2026
*   **Project Guide:** Dr. Rahul M. Dhokane
*   **Group Members:**
    1.  **Mr. Wakchaure Sanchit Sanjay** (Seat no- B400270167)
    2.  **Miss. Kale Jayshree Sandip** (Seat no- B400270126)
    3.  **Miss. Dange Shreya Rajesh** (Seat no- B400270113)
    4.  **Mr. Wakchaure Ganesh Shivaji** (Seat no- B400270166)

---

## 2. Project Directory Structure
*   `backend/` - The Python-based FastAPI backend server containing all API routes, feature extraction, ML prediction, and explanation code.
    *   `main.py` - Core entry point setting up routes, CORS, and starting the server on Uvicorn.
    *   `config.py` - Configuration and environment variables (database connection string, Gemini API key).
    *   `ml/` - Directory for machine learning files.
        *   `feature_extractor.py` - Extracts 28 structural, lexical, homograph, SSL, and keyword features.
        *   `predictor.py` - Singleton class that loads pre-trained models and makes predictions using a weighted ensemble + heuristics.
        *   `ensemble.py` - Contains the `WeightedEnsemble` class.
        *   `model_trainer.py` - Script to train models (Random Forest, XGBoost) and scaler on 120,000 URLs.
        *   `models/` - Folder containing the saved `.pkl` weights (`random_forest.pkl`, `xgboost_model.pkl`, `scaler.pkl`).
    *   `services/` - Core logic services.
        *   `url_scanner.py` - Orchestrates the URL scan (calls extractor, predictor, and maps attack types).
        *   `email_scanner.py` - Extracts URLs from email bodies and passes them to the URL scanner.
        *   `sms_scanner.py` - Analyzes SMS text for phishing patterns and urgency indicators.
        *   `feature_importance.py` - Evaluates the importance of each feature for SHAP/LIME-like local explanation.
        *   `explainer_service.py` - Generates user explanations using Gemini AI (structured narrative) or local rules as a fallback.
        *   `education_service.py` - Maps the scan results to actionable educational security tips.
        *   `supabase_service.py` - Integrates with PostgreSQL/Neon to store scan history and update user scores.
    *   `routers/` - Contains endpoint routers (`scan.py`, `dashboard.py`, `education.py`).
*   `frontend/` - The React-based user interface styled using standard CSS for maximum visual excellence and responsiveness.
    *   `src/` - React source code.
        *   `components/` - Visual widgets (Threat Meter Gauge, Explainer Card, Education Card, History Table).
        *   `pages/` - Application sections (Scanner, Dashboard, Education Library).
        *   `hooks/useScanner.js` - Centralized React hook managing scan state, HTTP calls, and local storage fallback.
        *   `services/api.js` - Axios instance for FastAPI communication.
*   `extension/` - Real-time browser plugin that intercepts requests (`chrome.runtime.onBeforeNavigate`) and uses the backend API to block malicious links before rendering.
*   `images/` - Contains core UML and system diagrams.
*   `screenshots/` - Contains visual proof of working UI components.

---

## 3. Technology Stack & Rationale

| Layer | Technology | Why Chosen? |
| :--- | :--- | :--- |
| **Frontend UI** | React + Vite | Fast, component-based rendering, responsive UI, hot reloading (via Vite), lightweight bundle. |
| **Backend API** | Python + FastAPI | Fast performance, automatic OpenAPI documentation (Swagger), native asynchronous support, clean integrations with Python ML packages. |
| **Database** | Neon PostgreSQL / Supabase | Relational data persistence, cloud-managed, reliable SQL syntax for storing complex scan logs and profile rankings. |
| **Machine Learning** | Scikit-learn, XGBoost | Industry-standard libraries for tabular data classification. XGBoost excels in speed and accuracy. |
| **Feature Extraction** | tldextract, python-whois | Accurate parsing of subdomains and Top-Level Domains (TLD); retrieves registered domain age from global WHOIS records. |
| **Explainable AI** | SHAP Concepts, Gemini API | SHAP calculates numeric feature contributions; Gemini translates mathematical vectors into readable explanations. |

---

## 4. System Workflows

### 4.1 URL Scanning Pipeline
1.  **Input:** User submits a URL through the React UI, or the Chrome extension intercepts a navigation event.
2.  **Validation:** The backend normalizes the URL (ensures proper schema: `http://` or `https://`).
3.  **Feature Extraction:** `URLFeatureExtractor` parses the URL into **28 specific features** across 6 groups.
4.  **Feature Optimization (RSTHFS):** Evaluates if the URL has redundant attributes and passes the minimal reduct subset to the ML models.
5.  **Ensemble Prediction:** Features are scaled using the saved `scaler.pkl`. Random Forest and XGBoost make independent predictions. A weighted sum determines the final score.
6.  **Heuristics Check:** If high-risk indicators are present (e.g., explicit homographs, raw IP host, brand names), the threat score is elevated to a default maximum (e.g., 85/100).
7.  **Attack Type Mapping:** Analyzes signals to label the attack (Homograph, Typosquatting, Brand Impersonation, Fake SSL, Urgency Manipulation, Credential Harvesting).
8.  **Explanation & Tips:** Explainer and Education services build narrative explanations and tips.
9.  **Persistence:** Saves the scan log into Neon PostgreSQL, updating the user's security score and "weak spots" count.
10. **Display:** Frontend receives a JSON payload and renders the Threat Meter, Explainer cards, and Education tips.

### 4.2 Email / SMS Scanning
*   **Email:** The backend extracts all embedded URLs using regex. Each URL goes through the URL scanning pipeline. The final email threat level is the maximum threat level among the found URLs, combined with text keyword analysis for urgency.
*   **SMS:** Scans for short URLs (bit.ly, tinyurl) and analyzes text features for financial requests and urgent action terms.

---

## 5. Under-the-Hood Algorithms & ML Core

### 5.1 The 28 Extracted Features
Features are grouped logically to capture structural, identity, and trust anomalies:
1.  **Domain-based (6):** Domain length, Subdomain count, IP address usage, Suspicious TLD (e.g., .tk, .xyz, .top), Brand name impersonation, Domain age.
2.  **Structure (8):** URL length, At (@) symbol, Double slash in path, Special character count, Digit ratio, Hyphen count, Dot count, Query parameter count.
3.  **Homograph (3):** Has look-alike chars, Homograph count, Unicode presence (IDN homograph attack signals).
4.  **SSL Trust (3):** HTTPS scheme, SSL certificate validity, SSL registration age score.
5.  **Keywords (5):** Login words, Secure words, Verification words, Update words, Urgency words.
6.  **Path/Redirect (3):** Path depth, Redirect keywords, Subdomain depth.

### 5.2 Feature Optimization via RSTHFS
*   **What it stands for:** Rough Set Theory-based Hybrid Feature Selection.
*   **Concept:** Phishing datasets often contain redundant or highly correlated features (e.g., subdomain count vs subdomain depth). High-dimensional data increases latency. RSTHFS identifies a **"minimal reduct"** (15-18 features) that maintains the classification performance.
*   **Workflow:**
    *   *Phase 1 (CDF-g Ranking):* Evaluates attributes using cumulative-distribution-function-gradients and information gain.
    *   *Phase 2 (Rough Set Aggregation):* Computes dependency rules and indiscernibility relations to extract the smallest subset that retains full accuracy.
*   **Benefit:** Reduces feature space by **68.7%** and backend inference speed to **< 50ms**, making it fast enough for a browser extension.

### 5.3 Stacking Ensemble (RF + XGBoost)
*   **Random Forest (RF):** A bagging classifier that builds multiple decision trees on random data subsets. Good at reducing variance.
*   **XGBoost:** A gradient boosting classifier that builds trees sequentially, correcting prior errors. Good at reducing bias and modeling complex boundary patterns.
*   **Ensemble Formula:**
    $$\text{Ensemble Probability} = (0.45 \times \text{RF Probability}) + (0.55 \times \text{XGBoost Probability})$$
*   **Heuristics Override:** An auxiliary rule-based security layer. For example, if a domain contains an explicit homograph character (e.g., `раурal.com` with a Cyrillic 'a'), the machine learning probability might not be 100% if the domain is old. The heuristics layer overrides this and locks the threat score to critical (>=85), ensuring safety-by-design.

### 5.4 Explainable AI (XAI) using SHAP & Gemini
*   **Why is it needed?** Standard ML models are black-boxes. They classify a site as "phishing" but don't explain *why*.
*   **SHAP (SHapley Additive exPlanations):** Assigns a numeric contribution score to each of the 28 features based on game theory. It answers: *"How much did the missing SSL certificate add to the threat score?"*
*   **Gemini AI Layer:** If a Gemini API key is configured, the backend passes the top suspicious features and threat metrics to Gemini. Gemini translates the mathematical features into a natural, user-friendly security report.
*   **Local Heuristics Fallback:** If the API key is not configured, the system uses static local templates in `explainer_service.py` to explain the risk factors (e.g., explaining why a raw IP host or look-alike letter is dangerous).

---

## 6. High-Frequency Viva Questions & Answers

### Q1: What is the novelty of your project?
**Answer:** The novelty lies in the **hybrid combination** of feature optimization, ensemble learning, and **Explainable AI (XAI)**. Traditional phishing detectors are binary classifiers (Safe/Phishing) and act as "black-boxes". PhantomShield:
1. Optimizes the feature space using Rough Set Theory (RSTHFS) to make it lightweight.
2. Combines Random Forest and XGBoost in a weighted ensemble with a safety-first heuristics override layer.
3. Translates machine learning feature weights into human-readable explanations using SHAP concepts and Gemini AI, transforming a security warning into an educational experience for the user.

### Q2: Why did you choose an ensemble model (Random Forest + XGBoost) instead of a single model?
**Answer:** Single models suffer from individual weaknesses. Random Forest is a Bagging algorithm that reduces overfitting and variance by averaging independent trees. XGBoost is a Boosting algorithm that reduces bias and increases accuracy by sequentially building trees that correct previous errors. Combining them with weights (45% RF, 55% XGBoost) balances bias and variance, achieving a peak validation accuracy of **98.2% to 98.4%**, which is higher than either model achieves individually.

### Q3: Explain what "RSTHFS" is and why it is critical for your project.
**Answer:** **RSTHFS** stands for *Rough Set Theory-based Hybrid Feature Selection*. 
When extraction compiles 28+ features, some are redundant. In a real-time system, especially a browser extension intercepting traffic, latency must be minimized. RSTHFS uses:
1. **CDF-g Ranking** to evaluate features by entropy reduction.
2. **Rough Set Aggregation** to find the "minimal reduct" (the smallest set of features that holds the same classification power).
In our implementation, it reduced feature space by over 60% and reduced runtime by 61%, lowering inference latency to **less than 50ms**, which makes real-time blocking feasible.

### Q4: How does your system detect Homograph Attacks?
**Answer:** A homograph attack uses characters from different alphabets (like Cyrillic or Greek) that look identical to Latin letters (e.g., Cyrillic 'а' replacing Latin 'a'). 
1. The `URLFeatureExtractor` normalizes the URL and checks for Unicode characters.
2. It uses a predefined `HOMOGRAPH_MAP` to detect substitutions.
3. It counts the look-alike characters and sets `has_homograph_chars = 1`.
4. If detected, the **heuristics layer** automatically overrides the ML score, setting the threat score to critical (minimum 85/100), as there is no legitimate reason for a domain name to mix alphabets to mimic a brand.

### Q5: What is Explainable AI (XAI) and how is it implemented?
**Answer:** XAI ensures machine learning decisions can be understood by humans. We implement it in two layers:
1. **Feature Importance Layer:** We calculate the relative contribution of each feature to the prediction score (similar to SHAP values).
2. **Natural Language Generation:** We pass the top 3-4 contributing features (e.g., missing SSL, short domain age, brand mismatch) to the `explainer_service.py`. If the Gemini API is active, it generates a narrative explaining the threat. If offline, it maps features to pre-written, user-friendly security explanations and suggests immediate safety actions.

### Q6: How does the email and SMS scanning work in comparison to URL scanning?
**Answer:** 
*   **URL Scanner:** Analyzes a single, explicit link using structural, lexical, SSL, and domain features.
*   **Email Scanner:** Uses regular expressions to parse the entire email body. It extracts all embedded URLs, scans each one, and rates the email's threat level based on the highest-scoring URL found. It also flags urgency language (e.g., "immediate action required").
*   **SMS Scanner:** Analyzes text for urgency keywords, financial requests, and extracts shortened URLs (e.g., bit.ly) which are common in SMS phishing (smishing).

### Q7: What database are you using and what is its schema?
**Answer:** We are using **Neon PostgreSQL** (accessed via Supabase libraries in Python). The schema contains two primary tables:
1.  `UserProfile`: Tracks the user statistics (total scans, safe scans, phishing caught, aggregated security score, and counts of weak spots like homograph or SSL failures).
2.  `ScanResult`: Stores details of individual scans (URL/message scanned, scan type, threat score, level, is_phishing, date, and detected attack types).
They are connected in a **one-to-many relationship**: one user profile can have many scan history entries.

### Q8: What are the limits of the current prototype?
**Answer:**
1.  **Semantic Content Analysis:** The current system focuses heavily on URL and domain properties rather than deep natural language understanding of the website's text body.
2.  **Attachment Scanning:** It does not inspect email file attachments (like malicious PDFs or executables).
3.  **Active Redirection:** It evaluates static URL patterns but does not execute the web page in a sandbox to trace multiple Javascript redirections.
These limits form our roadmap for Future Scope.

### Q9: How do your hardware and software requirements support real-world deployment?
**Answer:**
*   **Hardware:** The system runs on a standard processor (Intel i5 or higher) with 8GB RAM, because the optimized feature space (via RSTHFS) keeps memory usage low.
*   **Software:** Built on cross-platform frameworks (Python, Node.js). The FastAPI backend is packaged with Uvicorn, which can be deployed to cloud platforms (like Render or AWS). The React frontend is compiled to static files via Vite and can be hosted on Vercel or Netlify.

### Q10: How does the system handle backend disconnections?
**Answer:** The frontend implements a **Local Storage Fallback**. In `frontend/src/hooks/useScanner.js`, when a scan is requested and the backend is unreachable, the system retrieves cached scan results and history from the browser's `localStorage`. It displays a warning banner indicating that offline/cached data is being shown.

### Q11: What are your key experimental results?
**Answer:** In classification performance:
*   **Decision Tree:** ~94.3% accuracy.
*   **Random Forest:** ~97.8% accuracy.
*   **XGBoost:** ~98.7% accuracy.
*   **Proposed Ensemble (RF + XGBoost):** **99.2%** accuracy on our benchmark dataset of 120,000 URLs, showing that combining models yields superior performance.
*   **Latency:** The inference speed dropped from ~240ms to **92ms** (and down to 55ms in edge tests) after implementing RSTHFS feature reduction.

---

## 7. Viva Presentation Checklist & Tips
1.  **Keep it structured:** Start with the *Problem* (growing phishing sophistication, black-box filters) $\rightarrow$ explain your *Methodology* (feature extraction $\rightarrow$ RSTHFS $\rightarrow$ Stacking Ensemble $\rightarrow$ XAI explanation) $\rightarrow$ show the *Results* (99% accuracy, low latency) $\rightarrow$ conclude with *Future Work*.
2.  **Define abbreviations immediately:** Be ready to expand **RSTHFS**, **XAI**, **SHAP**, **TLD**, **SRS**, and **DFD**.
3.  **Use the diagrams:** When explaining the flow, refer directly to the **System Architecture Diagram** and **DFD Level 1** slides.
4.  **Emphasize Explainability:** Examiners love projects that go beyond simple classification. Explain how SHAP and Gemini help normal users understand cybersecurity risks.
