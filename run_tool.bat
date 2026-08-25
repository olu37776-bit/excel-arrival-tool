@echo off
setlocal
set "TOOL_DIR=%~dp0"
if not exist "%TOOL_DIR%.venv\Scripts\python.exe" (
  echo Please run setup_windows.bat first.
  pause
  exit /b 1
)
set /p "INPUT_FILE=Input Excel path: "
set /p "OUTPUT_FILE=Output Excel path: "
set /p "PREVIOUS_FILE=Previous result path (leave empty for first run): "
if "%PREVIOUS_FILE%"=="" (
  "%TOOL_DIR%.venv\Scripts\python.exe" -m revenue_tool run --input "%INPUT_FILE%" --output "%OUTPUT_FILE%" --config "%TOOL_DIR%config"
) else (
  "%TOOL_DIR%.venv\Scripts\python.exe" -m revenue_tool run --input "%INPUT_FILE%" --output "%OUTPUT_FILE%" --previous "%PREVIOUS_FILE%" --config "%TOOL_DIR%config"
)
pause

