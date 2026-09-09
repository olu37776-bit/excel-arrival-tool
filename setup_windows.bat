@echo off
setlocal EnableExtensions
title Excel Tool Setup
set "TOOL_DIR=%~dp0"
set "VENV_PY=%TOOL_DIR%.venv\Scripts\python.exe"

echo.
echo [1/3] Checking Python 3.10 or newer...
set "PY_CMD="
where py >nul 2>&1
if not errorlevel 1 (
  py -3 -c "import sys; sys.exit(0 if sys.version_info >= (3,10) else 1)" >nul 2>&1
  if not errorlevel 1 set "PY_CMD=py -3"
)
if defined PY_CMD goto python_ready

where python >nul 2>&1
if not errorlevel 1 (
  python -c "import sys; sys.exit(0 if sys.version_info >= (3,10) else 1)" >nul 2>&1
  if not errorlevel 1 set "PY_CMD=python"
)
if defined PY_CMD goto python_ready

echo ERROR: Python 3.10 or newer was not found.
echo Download Python from: https://www.python.org/downloads/windows/
echo During installation, enable "Add Python to PATH".
goto failed

:python_ready
echo Python is available.
echo.
echo [2/3] Creating or updating the local environment...
%PY_CMD% -m venv "%TOOL_DIR%.venv"
if errorlevel 1 (
  echo ERROR: Failed to create the local Python environment.
  goto failed
)

echo.
echo [3/3] Installing the Excel tool and dependencies...
"%VENV_PY%" -m pip install --upgrade "%TOOL_DIR%."
if errorlevel 1 (
  echo ERROR: Installation failed. Check the messages above and your network.
  goto failed
)

echo.
echo SETUP COMPLETED.
echo You can now double-click run_tool.bat.
echo.
pause
exit /b 0

:failed
echo.
echo SETUP FAILED. This window will remain open so you can read the error.
echo.
pause
exit /b 1
