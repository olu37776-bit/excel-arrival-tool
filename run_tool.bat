@echo off
setlocal
set "TOOL_DIR=%~dp0"
set "PYTHON_EXE=%TOOL_DIR%.venv\Scripts\python.exe"
if not exist "%PYTHON_EXE%" (
  echo Please run setup_windows.bat first.
  pause
  exit /b 1
)
set /p "LEGACY_FILE=Legacy Excel path: "
set /p "MONTHLY_FILE=Monthly order Excel path: "
set /p "DEMAND_FILE=Demand detail Excel path: "
set /p "TRANSIT_FILE=Country transit Excel path: "
set /p "OUTPUT_FILE=Output Excel path: "
set /p "PREVIOUS_FILE=Previous result path (empty for first run): "
if "%PREVIOUS_FILE%"=="" (
  "%PYTHON_EXE%" -m revenue_tool --legacy "%LEGACY_FILE%" --monthly-order "%MONTHLY_FILE%" --demand-detail "%DEMAND_FILE%" --transit "%TRANSIT_FILE%" --output "%OUTPUT_FILE%" --config "%TOOL_DIR%config\default.json"
) else (
  "%PYTHON_EXE%" -m revenue_tool --legacy "%LEGACY_FILE%" --monthly-order "%MONTHLY_FILE%" --demand-detail "%DEMAND_FILE%" --transit "%TRANSIT_FILE%" --output "%OUTPUT_FILE%" --previous "%PREVIOUS_FILE%" --config "%TOOL_DIR%config\default.json"
)
pause
