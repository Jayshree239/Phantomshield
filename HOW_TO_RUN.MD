BACKEND 
python -m uvicorn main:app --app-dir ".\backend" --reload --env-file ".\backend\.env" --host 0.0.0.0 --port 8000

FRONTEND
 npm run dev -- --host



ONE TIME SETUP GUIDE 
Use this exact first-time setup, fully inside a project virtual environment.

1. Create and activate venv (inside phantomshield folder)

Set-Location "d:\SPECTER\phantomshield"
py -3.10 -m venv .venv
& ".\.venv\Scripts\Activate.ps1"

2. Install backend dependencies in that venv only
python -m pip install --upgrade pip setuptools wheel
python -m pip install -r ".\backend\requirements.txt"
python -m pip check

3. Create backend env file
Copy-Item ".\backend\.env.example" ".\backend\.env" -Force

4. Confirm Python is from this venv
python -c "import sys; print(sys.executable)"

5. Run backend using venv Python
python -m uvicorn main:app --app-dir ".\backend" --reload --env-file ".\backend\.env" --host 0.0.0.0 --port 8000

6. In another terminal, run frontend
Set-Location "d:\SPECTER\phantomshield\frontend"
npm install
npm run dev -- --host

Important note:

Python packages are now strictly in project venv.
npm packages are local to frontend (node_modules), not global.