@echo off
:: ============================================================================
:: JARVIS Mark LVII - Run as Administrator Launcher
:: ============================================================================

net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [JARVIS] Administrator huquqlari soralmoqda...
    powershell -Command "Start-Process cmd -ArgumentList '/c cd /d \"%~dp0\" && python main.py' -Verb RunAs"
    exit /b
)

cd /d "%~dp0"
echo [JARVIS] Administrator huquqi bilan ishga tushirilmoqda...
python main.py
pause
