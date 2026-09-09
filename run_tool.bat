@echo off
setlocal EnableExtensions
title Excel Tool
set "TOOL_DIR=%~dp0"
set "PYTHON_EXE=%TOOL_DIR%.venv\Scripts\python.exe"
set "CONFIG_FILE=%TOOL_DIR%config\default.json"

echo.
echo Starting Excel Tool...
if not exist "%PYTHON_EXE%" (
  echo ERROR: The local environment is missing.
  echo Run setup_windows.bat first.
  goto failed
)
if not exist "%CONFIG_FILE%" (
  echo ERROR: Configuration file not found: %CONFIG_FILE%
  echo Download and extract the complete project again.
  goto failed
)

"%PYTHON_EXE%" -m revenue_tool.gui --config "%CONFIG_FILE%"
if errorlevel 1 (
  echo ERROR: The graphical window could not start.
  echo Review the error message above.
  goto failed
)
exit /b 0

:failed
echo.
pause
exit /b 1
