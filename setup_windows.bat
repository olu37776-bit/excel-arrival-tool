@echo off
chcp 65001 >nul
setlocal
set "TOOL_DIR=%~dp0"
py -3 -m venv "%TOOL_DIR%.venv"
if errorlevel 1 (
  echo Python 环境创建失败，请确认已安装 Python 3.10 或更高版本。
  pause
  exit /b 1
)
"%TOOL_DIR%.venv\Scripts\python.exe" -m pip install "%TOOL_DIR%."
if errorlevel 1 (
  echo 工具安装失败，请检查网络连接和错误信息。
  pause
  exit /b 1
)
echo 安装完成，可以双击 run_tool.bat 运行。
pause
