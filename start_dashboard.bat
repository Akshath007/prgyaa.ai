@echo off
title Pragyaa AI - Model STT Evaluation Dashboard
echo =================================================================
echo   Pragyaa AI - Speech-to-Text Telephony Evaluation Suite
echo =================================================================
echo.
echo Starting dashboard server on http://localhost:8501 ...
echo.

start "" "http://localhost:8501"
python "%~dp0run_dashboard.py"
pause
