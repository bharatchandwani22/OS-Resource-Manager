@echo off
REM ==============================================================================
REM Launch OS Resource Management Simulator Web Application
REM ==============================================================================

cd /d "%~dp0"
set PYTHONPATH=%~dp0;%PYTHONPATH%

echo ====================================================================
echo   LAUNCHING OS RESOURCE MANAGEMENT SIMULATOR WEB APPLICATION
echo   Access URL: http://127.0.0.1:5000
echo ====================================================================

python main.py --web --port 5000
pause
