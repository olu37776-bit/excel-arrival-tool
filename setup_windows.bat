@echo off
setlocal
set "TOOL_DIR=%~dp0"
py -3 -m venv "%TOOL_DIR%.venv"
if errorlevel 1 exit /b 1
"%TOOL_DIR%.venv\Scripts\python.exe" -m pip install --upgrade pip
"%TOOL_DIR%.venv\Scripts\python.exe" -m pip install "%TOOL_DIR%."
if errorlevel 1 exit /b 1
echo Setup completed. Run run_tool.bat to process an Excel file.
pause

