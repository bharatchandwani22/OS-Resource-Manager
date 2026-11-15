@echo off
REM ==============================================================================
REM OS Simulator Launcher (Windows CMD / Batch Entrypoint)
REM ==============================================================================

cd /d "%~dp0"
set PYTHONPATH=%~dp0;%PYTHONPATH%

python main.py %*
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Simulation exited with code %ERRORLEVEL%.
    pause
)
