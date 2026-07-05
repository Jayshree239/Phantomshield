# PhantomShield Run Guide (Windows)

This file explains exactly how to run the full project in simple steps:
- Backend (FastAPI)
- Frontend (React + Vite)
- Chrome Extension
- Neon database persistence

Project path used below:
- `d:\SPECTER\phantomshield`

## 1. Prerequisites

Install these first:
- Python 3.10 or 3.11
- Node.js 18+
- Google Chrome

## 2. Open project root

```powershell
Set-Location "d:\SPECTER\phantomshield"
```

## 3. One-time setup (venv + packages)

```powershell
# Create venv only if not already present
python -m venv .venv

# Backend dependencies
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r "backend\requirements.txt"
.\.venv\Scripts\python.exe -m pip check

# Frontend dependencies
Set-Location "d:\SPECTER\phantomshield\frontend"
npm install
Set-Location "d:\SPECTER\phantomshield"
```

Expected result for backend check:
- `No broken requirements found.`

If `pip check` reports old Supabase conflicts, run:

```powershell
.\.venv\Scripts\python.exe -m pip uninstall -y supabase postgrest supafunc gotrue realtime storage3
.\.venv\Scripts\python.exe -m pip check
```

## 4. Configure backend environment

Create env file:

```powershell
Copy-Item "backend\.env.example" "backend\.env"
```

Open `backend/.env` and set:
- `NEON_DATABASE_URL=<your_neon_connection_string>`
- `GEMINI_API_KEY=<optional>`

Notes:
- You can leave `DATABASE_URL` empty if `NEON_DATABASE_URL` is set.
- `ALLOWED_ORIGINS` is already in the correct JSON list format.

## 5. Apply DB schema in Neon

Run the SQL file in Neon SQL Editor:
- `supabase/schema.sql`

This schema is set up with RLS disabled and no active policies.

## 6. Start backend API (Terminal 1)

```powershell
Set-Location "d:\SPECTER\phantomshield\backend"
..\.venv\Scripts\python.exe -m uvicorn main:app --reload --env-file ".env" --host 0.0.0.0 --port 8000
```

Backend URLs:
- `http://localhost:8000/docs`
- `http://localhost:8000/health`

## 7. Start frontend (Terminal 2)

```powershell
Set-Location "d:\SPECTER\phantomshield\frontend"
npm run dev -- --host
```

Frontend URL:
- `http://localhost:5173`

## 8. Load Chrome extension

In Chrome:
1. Open `chrome://extensions`
2. Turn ON `Developer mode`
3. Click `Load unpacked`
4. Select `d:\SPECTER\phantomshield\extension`

## 9. Verify end-to-end (API + Neon)

From a new terminal, call scan API with `user_id` (required for DB save):

```powershell
Invoke-RestMethod -Uri "http://localhost:8000/api/scan/url" -Method Post -ContentType "application/json" -Body '{"url":"https://example.com","user_id":"demo_user"}'
```

Then verify in Neon SQL Editor:

```sql
SELECT COUNT(*) FROM scan_results;
SELECT COUNT(*) FROM user_profiles;
SELECT user_id, input_value, threat_level, created_at
FROM scan_results
ORDER BY created_at DESC
LIMIT 5;
```

If counts increase, DB persistence is working.

## 10. Verify extension behavior

With backend running:
1. Open a normal website tab (not `chrome://`)
2. Click the extension popup
3. Use `SCAN MANUALLY`
4. Confirm badge and result details update
5. Use `VIEW FULL REPORT` to open dashboard

## 11. Stop services

In both backend and frontend terminals:
- Press `Ctrl + C`

## Quick status rule

Project is fully running when:
- Backend is up on port 8000
- Frontend is up on port 5173
- Extension is loaded in Chrome
- Neon tables receive rows after scan with `user_id`
