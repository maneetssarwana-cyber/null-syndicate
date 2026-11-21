@echo off
title IndiePulse - Smart City Stray Triage & Municipal SLA Network
echo =====================================================================
echo  🐕 Starting IndiePulse (IndieGuard Engine)
echo  Autonomous Stray Triage, Rabies Early-Warning & Municipal SLA Network
echo =====================================================================

:: Change directory to current folder
cd /d "%~dp0"

echo [*] Starting FastAPI Backend & Command Center UI on http://127.0.0.1:8000 ...
python -m uvicorn api.main:app --host 127.0.0.1 --port 8000 --reload
pause
