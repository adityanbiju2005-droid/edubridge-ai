@echo off
title EduBridge AI — Frontend Server
cd /d "%~dp0frontend"
echo.
echo  ==========================================
echo   EduBridge AI Frontend — Starting...
echo   Open: http://127.0.0.1:5500
echo  ==========================================
echo.
echo  Make sure the backend is also running!
echo  (Run start_backend.bat in a separate window)
echo.
python -m http.server 5500
pause
