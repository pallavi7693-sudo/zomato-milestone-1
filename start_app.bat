@echo off
echo Starting GastroAI Backend (Flask)...
start "GastroAI Backend" cmd /k "cd /d "%~dp0" && .venv\Scripts\python web_app.py"

echo Starting GastroAI Frontend (Next.js)...
start "GastroAI Frontend" cmd /k "cd /d "%~dp0frontend-nextjs" && npm.cmd run dev"

echo Both services are starting up! You can close this window.
