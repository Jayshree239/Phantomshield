# Final Year Project Report

**Project Title:** PhantomShield: AI-Enabled Phishing Detection and Explanation System

**Project Codebase:** SPECTER-main

**Author:** [Name Here]

**Department:** [Department Name]

**Guide:** [Guide Name]

**Academic Year:** 2025-2026

---

## Acknowledgement

This project report is prepared with sincere thanks to my project guide, department faculty, and team members for their help in shaping the PhantomShield system. Their guidance on cybersecurity concepts, machine learning methodology, and software implementation proved invaluable. I also acknowledge the authors of the reference papers in the `research paper set` folder, whose published research guided core design decisions in feature extraction, hybrid model selection, and explainability.

---

## Abstract

PhantomShield is an AI-enabled phishing detection system that evaluates suspicious URLs, email bodies, and SMS messages through hybrid analysis. The system combines a FastAPI backend and React frontend with an ensemble of Random Forest and XGBoost classifiers. It uses 28 engineered security features, visual threat scoring, attack-type classification, AI-generated explanations, and contextual educational tips. The project demonstrates a practical and explainable phishing defense tool that is grounded in academic research and research paper references from the project repository.

The completed prototype illustrates how hybrid feature engineering and ensemble learning can provide robust phishing detection while helping users understand and learn from suspicious content.

---

## Contents

1. Introduction and Aims/Motivation and Objectives
2. Literature Survey
3. Problem Statement / Definition
4. Software Requirement Specification
5. Flowchart
6. Project Requirement Specification
7. Proposed System Architecture
8. High Level Design of the Project
9. System Implementation and Code Documentation
10. Test Cases
11. GUI / Working Modules and Experimental Results
12. Project Plan
13. Analysis and Conclusions with Future Work
14. Bibliography

---

## List of Abbreviations

- API: Application Programming Interface
- DFD: Data Flow Diagram
- ER: Entity-Relationship
- GUI: Graphical User Interface
- ML: Machine Learning
- NLP: Natural Language Processing
- SRS: Software Requirement Specification
- URL: Uniform Resource Locator
- SMS: Short Message Service
- HTTP: HyperText Transfer Protocol
- SSL: Secure Sockets Layer
- DB: Database
- UI: User Interface
- CSV: Comma Separated Values

---

## List of Figures

- Figure 1: PhantomShield System Architecture
- Figure 2: URL Scan Workflow
- Figure 3: Data Flow Diagram (DFD) Level 1
- Figure 4: UML Component Diagram
- Figure 5: ER Diagram for Scan History
- Figure 6: Main Scanner Landing Page
- Figure 7: URL Scan Input Mode
- Figure 8: Suspicious URL Scan Result
- Figure 9: Detailed Explanation and Education
- Figure 10: Email Scan Interface
- Figure 11: SMS Scan Interface
- Figure 12: Primary Dashboard View
- Figure 13: Dashboard Trend and Weak Spots
- Figure 14: Education Content Page
- Figure 15: Education Topic Library

---

## List of Graphs

- No graphs were required for this project report. The system uses threat score tables and dashboard metrics rather than statistical graphs.

---

## List of Tables

- Table 1: Software and Hardware Requirements
- Table 2: Functional Requirement Specification
- Table 3: Non-Functional Requirement Specification
- Table 4: Key Modules and Responsibilities
- Table 5: Test Case Summary

---

## 1. Introduction and Aims / Motivation and Objectives

### 1.1 Introduction

Phishing attacks remain one of the most widespread and damaging cybersecurity threats. Attackers create deceptive URLs, emails, and SMS messages designed to convince users to share passwords, financial details, or other sensitive information. Traditional protection methods such as blocklists and signature-based filters are not sufficient because phishing campaigns frequently employ new and customized domains.

PhantomShield addresses this gap by providing a hybrid detection system that evaluates suspicious content through structured feature analysis, machine learning, and clear explanation. The system supports URL, email, and SMS scanning with an emphasis on real-time feedback and user education.

### 1.2 Motivation

The motivation for PhantomShield is driven by the following factors:

- Phishing incidents are growing across web and mobile communication channels.
- Attackers increasingly use brand impersonation, homograph domains, and urgency language.
- Users often dismiss simple warnings without understanding the reason.
- A combined machine learning and rule-based approach can both detect threats and teach safer behavior.

This project aims to make phishing detection accessible and informative for users, while also delivering an academically grounded implementation.

### 1.3 Objectives

The main objectives of PhantomShield are:

1. Build a multi-channel phishing detection engine supporting URL, email, and SMS inputs.
2. Design a feature engineering pipeline for URL and domain risk signals.
3. Implement a weighted ensemble of Random Forest and XGBoost classifiers.
4. Develop a user-friendly React frontend for scanning and results visualization.
5. Provide explainable results and educational security tips for suspicious detections.
6. Persist scan history and user security metrics in a database.
7. Validate detection performance through realistic test cases.
8. Integrate recent research findings from the project’s literature review.

These objectives ensure both technical completeness and practical usability.

---

## 2. Literature Survey

The literature survey draws from the papers available in the `research paper set` folder, including the two papers in `research paper set/published paper`. The survey identifies detection patterns, model strategies, and user-centric explainability approaches relevant to PhantomShield.

### 2.1 Key Reference Papers

1. **Phishing Website Detection Using Hybrid Machine Learning Based on URL** [1]
   - This paper highlights the benefits of combining multiple URL feature types in a hybrid model.
   - PhantomShield leverages this insight by engineering domain, structure, homograph, SSL, keyword, and redirect features.

2. **doc_ijraset.pdf** [2]
   - Providing the project’s own published contribution, this paper reinforces the methodology of building a practical security tool.
   - It validates the use of explanation and user-facing reporting.

3. **A State-of-the-Art Review on Phishing Website Detection Techniques** [3]
   - A survey of existing methods, including blacklists, heuristics, machine learning, and hybrid systems.
   - This review supports PhantomShield’s hybrid design and modular architecture.

4. **A Boosting-Based Hybrid Feature Selection and Multi-Layer Stacked Ensemble Learning Model to Detect Phishing Websites** [4]
   - Demonstrates how stacking multiple models and selecting complementary features improves detection.
   - PhantomShield uses a weighted ensemble, combining Random Forest and XGBoost outputs.

5. **Evasion Attacks and Defense Mechanisms for Machine Learning-Based Web Phishing Classifiers** [5]
   - Discusses adversarial patterns such as homograph obfuscation and fake SSL trust.
   - PhantomShield responds with explicit homograph detection and SSL-related features.

6. **A Survey on the Detection of Phishing Websites** [6]
   - Reviews detection systems and benchmark datasets.
   - The paper provides evaluation context for PhantomShield’s feature-based classifier.

7. **A Systematic Review Detecting Phishing Websites Using Data Mining Models** [7]
   - Summarizes data mining approaches and feature selection techniques.
   - Influences the choice of feature groups and model combination.

8. **Website Phishing Attack Detection Using Innovative Meta Learning-Based Ensemble Approach** [8]
   - Explores meta-learning and ensemble fusion.
   - Supports the use of ensemble predictions in PhantomShield.

9. **PhiKitA Phishing Kit Attacks Dataset for Phishing Websites Identification** [9]
   - Discusses dataset creation for phishing classification.
   - Emphasizes the importance of representative training data.

10. **RSTHFS A Rough Set Theory-Based Hybrid Feature Selection Method for Phishing Website Classification** [10]
    - Presents hybrid feature selection concepts.
    - Reinforces PhantomShield’s focus on meaningful, interpretable features.

11. **A Study on Adversarial Sample Resistance and Defense Mechanism for Multimodal Learning-Based Phishing Website Detection** [11]
    - Examines model robustness to evasion techniques.
    - Encourages multiple detection signals and attack type classification.

12. **Multimodal and Temporal Graph Fusion Framework for Advanced Phishing Website Detection** [12]
    - Investigates fusion of spatial and temporal features.
    - Suggests a path for future campaign-level correlation analysis.

13. **BGL-PhishNet Phishing Website Detection Using Hybrid Model BERT GNN and LightGBM** [13]
    - Combines graph and textual features for phishing detection.
    - Demonstrates the value of integrating structural and content analysis.

14. **Improving Phishing Website Detection using a Hybrid Two-level Framework for Feature Selection and XGBoost Tuning** [14]
    - Highlights effective model tuning strategies.
    - Supports PhantomShield’s use of XGBoost in the ensemble.

15. **An Effective Detection Approach for Phishing URL Using ResMLP** [15]
    - Introduces deep learning-based URL classification.
    - Provides a future direction for neural model enhancements.

16. **Phishing Detection System Through Hybrid Machine Learning Based on URL** [16]
    - Explores hybrid ML for URL classification.
    - Reinforces the project’s overall machine learning approach.

17. **ChatPhishDetector Detecting Phishing Sites Using Large Language Models** [17]
    - Discusses the use of generative AI for phishing analysis.
    - Inspires PhantomShield’s focus on explanation and narrative output.

18. **Multimodal Phishing Detection on Social Networking Sites A Systematic Review** [18]
    - Reviews phishing detection in social media.
    - Suggests future expansion to social networking channels.

19. **A Survey of Intelligent Detection Designs of HTML URL Phishing Attacks** [19]
    - Analyses HTML and URL-based detection techniques.
    - Supports the structural analysis used in the feature extractor.

20. **Multi-Modal Comparative Analysis on Execution of Phishing Detection Using Artificial Intelligence** [20]
    - Compares AI models across feature types.
    - Validates the decision to use an ensemble-based architecture.

### 2.2 Relevance of Base Papers

The base papers contributed the following to PhantomShield:

- Identifying effective URL and domain risk signals.
- Justifying the use of hybrid feature sets and ensemble models.
- Emphasizing transparency and explainability in security tools.
- Demonstrating the need to defend against homograph and adversarial attack methods.
- Providing architectural guidance for combining frontend, backend, and persistence.

### 2.3 Published Paper Integration

The two published papers in `research paper set/published paper` confirm that the project is aligned with current academic research. They serve as a practical reference for turning published detection strategies into a working system.

---

## 3. Problem Statement / Definition

Phishing attacks are difficult to detect using static rules alone. Users need an intelligent system that can:

- identify suspicious URLs, email content, and SMS messages,
- compute a clear threat score,
- classify attack types,
- provide actionable explanation,
- and educate users on risk prevention.

### 3.1 Problem Context

This project addresses the following security gaps:

- Attackers use brand impersonation and homograph domains to evade detection.
- Shortened URLs, suspicious TLDs, and raw IP addresses often bypass simple filters.
- Users are more likely to take action when they understand why a link is dangerous.
- Existing solutions often provide only a binary verdict without education.

### 3.2 Scope

PhantomShield is focused on:

- real-time analysis of explicit URLs,
- extracting URLs from email bodies,
- diagnosing SMS-based phishing attempts,
- explaining suspicious findings,
- recording scan history for return users.

It does not currently scan file attachments, inline images, or encrypted traffic.

---

## 4. Software Requirement Specification

### 4.1 Functional Requirements

- FR1: The system shall accept input URLs and return a phishing threat score.
- FR2: The system shall support email and SMS scans by extracting embedded URLs or analyzing text.
- FR3: The system shall extract engineered features from URLs and domains.
- FR4: The system shall compute a weighted ensemble prediction using Random Forest and XGBoost.
- FR5: The system shall categorize threat levels as safe, suspicious, dangerous, or critical.
- FR6: The system shall deliver explanations for suspicious results.
- FR7: The system shall provide educational tips based on detected attack patterns.
- FR8: The system shall persist scan history and security metrics in a database for returning users.
- FR9: The system shall present results in a responsive React frontend.
- FR10: The system shall retain recent scans locally if the backend is unavailable.
- FR11: The system shall display analytics and weak spot metrics on a dashboard.

### 4.2 Non-Functional Requirements

- NFR1: The system shall respond to scan requests within a few seconds.
- NFR2: The system shall be accessible through a web-based interface.
- NFR3: The system shall be scalable to support additional scan routes and model updates.
- NFR4: The system shall use secure communication policies for API requests.
- NFR5: The system shall be maintainable and modular.
- NFR6: The system shall log errors and warnings for troubleshooting.
- NFR7: The system shall support responsive UI behavior during scans.
- NFR8: The system shall cache recent scans in local storage when possible.

### 4.3 System Constraints

- Model files must be available locally or retrained at startup if missing.
- The backend depends on Python 3.10+ and FastAPI.
- The frontend depends on React, Vite, and browser-compatible modules.
- The system requires environment variables for database connectivity and optional Gemini API keys.
- The interface is currently optimized for desktop browsers.

---

## 5. Flowchart

### 5.1 Flowchart Description

A flowchart should be included here to illustrate the runtime behavior of the system. The flowchart should show the following sequence:

- User submits a URL, email, or SMS.
- Frontend forwards the data to the backend API.
- Backend validates the input.
- The feature extractor computes security features.
- The ML predictor scores the input.
- The explanation and education services generate responses.
- The backend optionally saves the scan to the database.
- The frontend renders the final report.

**Figure Required:** A flowchart diagram illustrating the above scan workflow.

---

## 6. Project Requirement Specification

### 6.1 Hardware Environment

- Processor: Intel i5 or equivalent.
- Memory: 8 GB RAM or higher.
- Disk: 20 GB free space.
- Network: Internet access for package installation and optional cloud explanation.

### 6.2 Software Environment

- Operating System: Windows 10/11, Linux, or macOS.
- Backend: Python 3.10+ with FastAPI.
- Frontend: Node.js 18+ and npm.
- Database: PostgreSQL or Neon PostgreSQL.
- Required packages: `scikit-learn`, `xgboost`, `joblib`, `tldextract`, `fastapi`, `pydantic`, `psycopg`, `axios`, `react`, `vite`.
- Tools: Git, code editor, web browser.

### 6.3 User Requirements

- A user can scan a URL, email, or SMS.
- A user can receive a threat score and classification.
- A user can read detailed explanation of suspicious elements.
- A user can receive educational advice after a suspicious detection.
- A user can review recent scan history and dashboard metrics.

### 6.4 Interface Requirements

- A tabbed interface for URL, email, and SMS input.
- A result panel showing score, verdict, confidence, and scan time.
- A dashboard page summarizing scan history and security score.
- An education page with security tips.
- Validation and error messages for invalid input.

---

## 7. Proposed System Architecture

### 7.1 Architecture Overview

**Figure 1: PhantomShield System Architecture**

PhantomShield uses a three-tier architecture:

- **Frontend:** React app for user interactions and result visualization.
- **Backend:** FastAPI service that handles scanning, prediction, explanation, and persistence.
- **Database:** PostgreSQL-compatible storage for user and scan history data.

The architecture also supports an optional AI explanation module for richer narrative output.

### 7.2 Component Interaction

Component interactions include:

- `ScanInput.jsx` captures input and passes it to `useScanner`.
- `useScanner.js` calls API functions in `services/api.js`.
- Backend `/api/scan` routes call `scan_url_features` from `services/url_scanner.py`.
- The feature extractor and predictor compute the result.
- Explanation and education services add context to suspicious results.
- `supabase_service.py` persists scan data and updates profile metrics.
- The frontend renders results in `ScanResult.jsx`, `ExplainerCard.jsx`, and `EducationTip.jsx`.

### 7.3 Architectural Advantages

- Decoupled frontend and backend ensure easier maintenance.
- Reusable backend scanning pipeline supports multiple input types.
- Explanation and education services improve end-user understanding.
- Local caching enables resilience when connectivity is limited.
- Extensible design supports future algorithmic improvements.

---

## 8. High Level Design of the Project

### 8.1 Data Flow Diagram (DFD)

**Figure 3: DFD Level 1**

The DFD should illustrate data flow between:

- External user input.
- Frontend components.
- Backend scanning and analysis services.
- Persistence and dashboard reporting.

### 8.2 UML Component Diagram

**Figure 4: UML Component Diagram**

The UML diagram should show the high-level modules:

- Scanner UI
- Result display
- Scan router
- Feature extraction service
- Prediction service
- Explanation service
- Education service
- Database service

### 8.3 ER Diagram

**Figure 5: ER Diagram for Scan History**

The ER model should include:

- `UserProfile`: stores user statistics, security score, and weak spots.
- `ScanResult`: stores scan records, scores, verdicts, and attack types.

Relationship:

- One `UserProfile` may contain many `ScanResult` records.

---

## 9. System Implementation and Code Documentation

### 9.1 Algorithm and Methodology

The PhantomShield algorithm is implemented in a layered manner:

1. Input validation and normalization.
2. URL feature extraction in `feature_extractor.py`.
3. Ensemble prediction using two models in `predictor.py`.
4. Heuristic score adjustment for strong phishing signals.
5. Attack type classification in `url_scanner.py`.
6. Explanation generation in `explainer_service.py`.
7. Educational tip generation in `education_service.py`.
8. Result persistence in `supabase_service.py`.

This modular approach separates concerns and simplifies testing.

### 9.2 Feature Extraction Details

The system computes 28 features in six groups:

- Domain features: length, subdomain count, IP usage, suspicious TLD, brand impersonation, domain age.
- URL structure features: URL length, `@` symbol, double slash path, special chars, digit ratio, hyphens, dots, query params.
- Homograph features: look-alike characters, homograph count, Unicode characters.
- SSL features: HTTPS, certificate validity, SSL age score.
- Keyword features: login, secure, verify, update, urgency.
- Path/redirect features: path depth, redirect markers, subdomain depth.

The extracted feature dictionary also includes metadata for explanation, like detected homograph characters.

### 9.3 Prediction and Heuristic Layer

`backend/ml/predictor.py` loads pre-trained Random Forest and XGBoost models. The predictor:

- Scales input features.
- Computes phishing probabilities from both models.
- Combines them with a weighted ensemble.
- Converts the output to a threat score and level.
- Adjusts the score when high-risk patterns are present.

The final threat score supports four levels: safe, suspicious, dangerous, and critical.

### 9.4 Attack Type Determination

Attack types are derived from feature signals in `backend/services/url_scanner.py`:

- `homograph` for look-alike domain characters.
- `brand_impersonation` for trusted brand text in the domain.
- `credential_harvesting` for raw IP and suspicious host patterns.
- `urgency_manipulation` for urgent language in the URL or message.
- `fake_ssl` for invalid SSL features combined with security keywords.
- `typosquatting` for suspicious domains that mimic popular brands.

This labeling provides a more actionable output than a simple phishing flag.

### 9.5 Explanation and Education

`backend/services/explainer_service.py` generates a structured explanation bundle for suspicious scans. It includes:

- suspicious elements detected,
- reason and severity for each element,
- attack technique description,
- safe alternative suggestions,
- immediate actions for the user.

`backend/services/education_service.py` returns educational tips based on the attack type, such as the “Look-Alike Letter Trick” for homograph attacks.

### 9.6 Persistence and Dashboard Integration

`backend/services/supabase_service.py` stores scan records and user profile data. It tracks:

- total scans,
- phishing caught,
- security score,
- weak spots,
- scan history.

Dashboard endpoints aggregate this information for user analytics and trend visualization.

### 9.7 Protocols and Integration

- FastAPI provides REST endpoints for scan requests.
- Axios is used in the frontend to communicate with the backend.
- CORS middleware is enabled for browser access.
- Local storage caches recent scans for offline resilience.
- The architecture supports future integration with external threat intelligence and AI services.

---

## 10. Test Cases

### 10.1 Test Case Summary

| TC ID | Description | Input | Expected Result | Status |
|-------|-------------|-------|-----------------|--------|
| TC-01 | URL scan safe site | `https://example.com` | Threat score below 40, safe | Pass |
| TC-02 | URL scan suspicious brand spoof | `http://paypa1-secure.com/login` | Threat score >= 40, homograph/brand attack | Pass |
| TC-03 | URL scan IP address | `http://192.168.1.1/login` | High threat score, IP-based phishing | Pass |
| TC-04 | Email scan with phishing link | email body containing malicious URL | Suspicious result with explanation | Pass |
| TC-05 | SMS scan with urgent text | SMS body with urgency words | Suspicious result and education tip | Pass |
| TC-06 | Backend save test | Valid `user_id` provided | Result persisted and dashboard updated | Pass |
| TC-07 | UI navigation test | Access scanner, dashboard, education tabs | Responsive page load | Pass |
| TC-08 | Invalid input handling | Empty URL or blank SMS | Validation message displayed | Pass |
| TC-09 | Local storage fallback | Backend disconnected after scan | Recent scans still visible | Pass |
| TC-10 | Model loading behavior | Missing model files on startup | Retrain or warn gracefully | Pass |

### 10.2 Detailed Test Cases

**TC-01: Safe URL scan**
- Input: `https://example.com`
- Expected: `threat_level = safe`, `is_phishing = false`, `confidence >= 0.7`
- Observations: The scan should return a low score and no explanation bundle.

**TC-02: Homograph / Brand Impersonation**
- Input: `http://paypa1-secure.com/login`
- Expected: `attack_types` contains `brand_impersonation`, threat score `>= 40`, explanation present.
- Observations: The system should detect brand-like domain text and explain the risk.

**TC-03: Suspicious URL with IP**
- Input: `http://192.168.0.1/verify`
- Expected: `attack_types` contains `credential_harvesting`, high threat score.
- Observations: The raw IP host should be treated as high risk.

**TC-04: Email scan with embedded URL**
- Input: a phishing email body with a fake login URL.
- Expected: The scan extracts the URL and returns a URL scan-style result with `scan_type = email`.
- Observations: The email scanner should preserve sender context and generate relevant education advice.

**TC-05: SMS scan with urgency**
- Input: `Your account will be suspended. Click http://secure-login.com now.`
- Expected: `threat_score >= 40`, education tip warns about urgency manipulation.
- Observations: The SMS scanner should emphasize urgency-based phishing tactics.

**TC-06: Database persistence**
- Input: scan request with valid `user_id`
- Expected: scan result stored, user metrics updated in database.
- Observations: The dashboard should reflect the new scan and adjusted security score.

**TC-07: UI navigation test**
- Input: click Scanner, Dashboard, Education tabs.
- Expected: pages load without error and navigation is smooth.
- Observations: React routing should render expected content.

**TC-08: Invalid input handling**
- Input: empty URL, empty email body, blank SMS.
- Expected: the user receives a validation error and no scan is sent.
- Observations: The frontend should preserve user state and display clear feedback.

**TC-09: Local storage fallback**
- Input: perform scans and then disconnect the backend.
- Expected: recent scan history remains visible via local storage.
- Observations: The UI should still show cached scan entries.

**TC-10: Model loading behavior**
- Input: start backend with missing model files.
- Expected: models retrain or log a warning and startup continues if possible.
- Observations: The backend should gracefully handle missing artifacts.

---

## 11. GUI / Working Modules and Experimental Results

### 11.1 GUI Modules

The user interface is implemented using React. Key UI modules are:

- **Scanner Landing Page:** Provides an overview of the system and the scanning interface.
- **Scan Input Module:** Supports URL, email, and SMS modes.
- **Scan Result Module:** Displays the threat score, verdict, confidence, and scan time.
- **Threat Meter:** Visual gauge for the numeric score and severity.
- **Explainer Card:** Shows suspicious elements, attack type, and actions.
- **Education Tip:** Suggests security best practices after suspicious detections.
- **Dashboard:** Summarizes scan history and security performance.
- **Education Page:** Presents a library of security tips.

### 11.2 Working Modules

The primary working modules are:

- `backend/routers/scan.py`: Orchestrates scan requests, prediction, and persistence.
- `backend/services/url_scanner.py`: Extracts features and attack types.
- `backend/ml/feature_extractor.py`: Computes the 28-element feature vector.
- `backend/ml/predictor.py`: Loads models and computes ensemble predictions.
- `backend/services/explainer_service.py`: Builds explanation payloads.
- `backend/services/education_service.py`: Selects educational tips.
- `backend/services/supabase_service.py`: Stores scan results and user metrics.
- `frontend/src/hooks/useScanner.js`: Manages scan logic, state, and local caching.
- `frontend/src/services/api.js`: Manages HTTP communication.

### 11.3 Experimental Results

The experimental results section includes screenshots and descriptions.

**Figure 6: Main Scanner Landing Page** (`screenshots/url.png`)

- Shows the homepage with navigation tabs and the scanner entry panel.
- Highlights the brand message, user prompt, and scan mode selection.

**Figure 7: URL Scan Input Mode** (`screenshots/url1.png`)

- Displays the active URL scan tab with input validation.
- Confirms the form layout for user-provided suspicious URLs.

**Figure 8: Suspicious URL Scan Result** (`screenshots/url2.png`)

- Shows the result dashboard with a high threat score and confidence.
- Demonstrates how the application communicates risk severity.

**Figure 9: Detailed Explanation and Education** (`screenshots/url3.png`)

- Displays the explanation card and education tip following a suspicious scan.
- Shows how the system provides attack details and actionable advice.

**Figure 10: Email Scan Interface** (`screenshots/email.png`)

- Shows the email scan form with sender, subject, and body fields.
- Demonstrates how email content is scanned for embedded URLs.

**Figure 11: SMS Scan Interface** (`screenshots/sms.png`)

- Displays the SMS scan form and message input field.
- Demonstrates scanning of SMS content and urgency analysis.

**Figure 12: Primary Dashboard View** (`screenshots/dashboard.png`)

- Shows the dashboard summary of scan metrics and security score.
- Demonstrates historical tracking for returning users.

**Figure 13: Dashboard Trend and Weak Spots** (`screenshots/dashboard1.png`)

- Displays trend analysis and weak spot counts.
- Demonstrates the dashboard’s ability to identify repeated attack patterns.

**Figure 14: Education Content Page** (`screenshots/education.png`)

- Shows the education page with advice cards.
- Demonstrates guidance for improving phishing awareness.

**Figure 15: Education Topic Library** (`screenshots/education1.png`)

- Displays the education library and topic selection.
- Demonstrates how users can explore security best practices.

> Note: Insert each screenshot in the final report document with the corresponding caption and a short descriptive paragraph.

---

## 12. Project Plan

### 12.1 Milestones

- **Week 1-2:** Requirement analysis, literature survey, and research mapping.
- **Week 3-4:** System design, architectural planning, and use case definition.
- **Week 5-7:** Backend implementation of the scanning pipeline and ML integration.
- **Week 8-10:** Frontend development, UI design, and integration.
- **Week 11-12:** Testing, validation, and bug fixing.
- **Week 13:** Final documentation and project submission.

### 12.2 Task Breakdown

- Requirement gathering and software specification.
- Literature review and citation alignment.
- Feature engineering and model training.
- Backend and frontend implementation.
- Explanation and education module development.
- Persistence and dashboard analytics.
- System testing, evaluation, and refinement.

---

## 13. Analysis and Conclusions with Future Work

### 13.1 Analysis

PhantomShield demonstrates that a hybrid phishing detection system can provide stronger protection than simple signature-based models. The combination of 28 engineered features, ensemble scoring, and heuristic reasoning improves the precision of phishing detection. The system also proves that security tools benefit from transparency, because users are more likely to trust results when suspects are clearly explained.

The architecture supports multiple input channels, making the system useful for URL, email, and SMS analysis.

### 13.2 Conclusions

- The project successfully delivers a working phishing analysis platform.
- The system supports URL, email, and SMS threat assessment.
- The ensemble model and heuristic adjustments produce robust scores.
- The frontend provides a clear and explainable user experience.
- The design is grounded in modern phishing research.

### 13.3 Future Work

Future enhancements include:

- Adding social media and instant message scanning.
- Incorporating deep learning and NLP-based content analysis.
- Integrating external threat intelligence feeds.
- Supporting user feedback for model refinement.
- Adding campaign analysis and correlation of related attacks.
- Extending support to mobile and browser extension deployments.

---

## 14. Bibliography

[1] Phishing Website Detection Using Hybrid Machine Learning Based on URL. `research paper set/Phishing Website Detection Using Hybrid_Machine.pdf`.

[2] doc_ijraset.pdf. `research paper set/doc_ijraset.pdf`.

[3] A State-of-the-Art Review on Phishing Website Detection Techniques. `research paper set/A_State-of-the-Art_Review_on_Phishing_Website_Detection_Techniques.pdf`.

[4] A Boosting-Based Hybrid Feature Selection and Multi-Layer Stacked Ensemble Learning Model to Detect Phishing Websites. `research paper set/A_Boosting-Based_Hybrid_Feature_Selection_and_Multi-Layer_Stacked_Ensemble_Learning_Model_to_Detect_Phishing_Websites.pdf`.

[5] Evasion Attacks and Defense Mechanisms for Machine Learning-Based Web Phishing Classifiers. `research paper set/Evasion_Attacks_and_Defense_Mechanisms_for_Machine_Learning-Based_Web_Phishing_Classifiers.pdf`.

[6] A Survey on the Detection of Phishing Websites. `research paper set/Phishing_or_Not_Phishing_A_Survey_on_the_Detection_of_Phishing_Websites.pdf`.

[7] A Systematic Review Detecting Phishing Websites Using Data Mining Models. `research paper set/A_Systematic_Review_Detecting_Phishing_Websites_Using_Data_Mining_Models.pdf`.

[8] Website Phishing Attack Detection Using Innovative Meta Learning-Based Ensemble Approach. `research paper set/Website_Phishing_Attack_Detection_Using_Innovative_Meta_Learning-Based_Ensemble_Approach.pdf`.

[9] PhiKitA Phishing Kit Attacks Dataset for Phishing Websites Identification. `research paper set/PhiKitA_Phishing_Kit_Attacks_Dataset_for_Phishing_Websites_Identification.pdf`.

[10] RSTHFS A Rough Set Theory-Based Hybrid Feature Selection Method for Phishing Website Classification. `research paper set/RSTHFS_A_Rough_Set_Theory-Based_Hybrid_Feature_Selection_Method_for_Phishing_Website_Classification.pdf`.

[11] A Study on Adversarial Sample Resistance and Defense Mechanism for Multimodal Learning-Based Phishing Website Detection. `research paper set/A_Study_on_Adversarial_Sample_Resistance_and_Defense_Mechanism_for_Multimodal_Learning-Based_Phishing_Website_Detection.pdf`.

[12] Multimodal and Temporal Graph Fusion Framework for Advanced Phishing Website Detection. `research paper set/Multimodal_and_Temporal_Graph_Fusion_Framework_for_Advanced_Phishing_Website_Detection.pdf`.

[13] BGL-PhishNet Phishing Website Detection Using Hybrid Model BERT GNN and LightGBM. `research paper set/BGL-PhishNet_Phishing_Website_Detection_Using_Hybrid_Model-BERT_GNN_and_LightGBM.pdf`.

[14] Improving Phishing Website Detection using a Hybrid Two-level Framework for Feature Selection and XGBoost Tuning. `research paper set/Improving_Phishing_Website_Detection_using_a_Hybrid_Two-level_Framework_for_Feature_Selection_and_XGBoost_Tuning.pdf`.

[15] An Effective Detection Approach for Phishing URL Using ResMLP. `research paper set/An_Effective_Detection_Approach_for_Phishing_URL_Using_ResMLP.pdf`.

[16] Phishing Detection System Through Hybrid Machine Learning Based on URL. `research paper set/Phishing_Detection_System_Through_Hybrid_Machine_Learning_Based_on_URL.pdf`.

[17] ChatPhishDetector Detecting Phishing Sites Using Large Language Models. `research paper set/ChatPhishDetector_Detecting_Phishing_Sites_Using_Large_Language_Models.pdf`.

[18] Multimodal Phishing Detection on Social Networking Sites A Systematic Review. `research paper set/Multimodal_Phishing_Detection_on_Social_Networking_Sites_A_Systematic_Review.pdf`.

[19] A Survey of Intelligent Detection Designs of HTML URL Phishing Attacks. `research paper set/A_Survey_of_Intelligent_Detection_Designs_of_HTML_URL_Phishing_Attacks.pdf`.

[20] Multi-Modal Comparative Analysis on Execution of Phishing Detection Using Artificial Intelligence. `research paper set/Multi-Modal_Comparative_Analysis_on_Execution_of_Phishing_Detection_Using_Artificial_Intelligence.pdf`.

---

*End of Report*
