@echo off
setlocal
set "TOOL_DIR=%~dp0"
set "PYTHON_EXE=%TOOL_DIR%.venv\Scripts\python.exe"
if not exist "%PYTHON_EXE%" (
  echo Please run setup_windows.bat first.
  pause
  exit /b 1
)
set /p "INPUT_FILE=Current business Excel path: "
set /p "OUTPUT_FILE=Output Excel path: "
set /p "PREVIOUS_FILE=Previous result path (empty for first run): "
if "%PREVIOUS_FILE%"=="" (
  "%PYTHON_EXE%" -m revenue_tool --input "%INPUT_FILE%" --output "%OUTPUT_FILE%" --config "%TOOL_DIR%config\default.json"
) else (
  "%PYTHON_EXE%" -m revenue_tool --input "%INPUT_FILE%" --output "%OUTPUT_FILE%" --previous "%PREVIOUS_FILE%" --config "%TOOL_DIR%config\default.json"
)
pause

