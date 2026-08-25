@echo off
setlocal
set "TOOL_DIR=%~dp0"
py -3 -m venv "%TOOL_DIR%.venv"
if errorlevel 1 (
  echo Python environment creation failed.
  pause
  exit /b 1
)
"%TOOL_DIR%.venv\Scripts\python.exe" -m pip install "%TOOL_DIR%."
if errorlevel 1 (
  echo Tool installation failed.
  pause
  exit /b 1
)
echo Setup completed.
pause

