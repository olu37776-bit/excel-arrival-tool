@echo off
chcp 65001 >nul
setlocal
set "TOOL_DIR=%~dp0"
set "PYTHON_EXE=%TOOL_DIR%.venv\Scripts\python.exe"
if not exist "%PYTHON_EXE%" (
  echo 请先双击运行 setup_windows.bat 完成安装。
  pause
  exit /b 1
)
echo 请依次粘贴完整文件路径；可直接粘贴 Windows 的“复制为路径”结果。
set /p "LEGACY_FILE=1. 遗留量 Excel："
set /p "MONTHLY_FILE=2. 当月订货 Excel："
set /p "DEMAND_FILE=3. 要货明细 Excel："
set /p "TRANSIT_FILE=4. 国家运输周期 Excel："
set /p "OUTPUT_FILE=5. 输出 Excel（必须包含文件名.xlsx）："
set /p "PREVIOUS_FILE=6. 上一次成功结果（首次运行直接回车）："
set "LEGACY_FILE=%LEGACY_FILE:"=%"
set "MONTHLY_FILE=%MONTHLY_FILE:"=%"
set "DEMAND_FILE=%DEMAND_FILE:"=%"
set "TRANSIT_FILE=%TRANSIT_FILE:"=%"
set "OUTPUT_FILE=%OUTPUT_FILE:"=%"
set "PREVIOUS_FILE=%PREVIOUS_FILE:"=%"
if "%PREVIOUS_FILE%"=="" (
  "%PYTHON_EXE%" -m revenue_tool --legacy "%LEGACY_FILE%" --monthly-order "%MONTHLY_FILE%" --demand-detail "%DEMAND_FILE%" --transit "%TRANSIT_FILE%" --output "%OUTPUT_FILE%" --config "%TOOL_DIR%config\default.json"
) else (
  "%PYTHON_EXE%" -m revenue_tool --legacy "%LEGACY_FILE%" --monthly-order "%MONTHLY_FILE%" --demand-detail "%DEMAND_FILE%" --transit "%TRANSIT_FILE%" --output "%OUTPUT_FILE%" --previous "%PREVIOUS_FILE%" --config "%TOOL_DIR%config\default.json"
)
pause
