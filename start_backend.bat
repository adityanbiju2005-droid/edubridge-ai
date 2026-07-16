@echo off
title EduBridge AI — Backend Server
cd /d "%~dp0backend"
echo.
echo  ==========================================
echo   EduBridge AI Backend — Starting...
echo   API: http://127.0.0.1:8000
echo   Docs: http://127.0.0.1:8000/docs
echo  ==========================================
echo.
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
pause
