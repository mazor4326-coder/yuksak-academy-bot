@echo off
title OMAVIY2026 Bot Starter
cd /d "%~dp0"
echo ========================================
echo   STARTING OMAVIY2026 AD-POSTING BOT
echo ========================================
echo.

:: Check if already running
if exist bot.pid (
    set /p PID=<bot.pid
    tasklist /FI "PID eq %PID%" 2>nul | findstr %PID% >nul
    if %errorlevel% equ 0 (
        echo [!] Bot is already running with PID %PID%.
        echo [!] Please stop it first using STOP_BOT.bat or restart it.
        echo.
        pause
        exit
    )
)

:: Find python executable path
set "PYTHON_EXE="

if exist "C:\Temp\python_embed\python.exe" (
    set "PYTHON_EXE=C:\Temp\python_embed\python.exe"
) else (
    python --version >nul 2>&1
    if %errorlevel% equ 0 (
        set "PYTHON_EXE=python"
    )
)

if "%PYTHON_EXE%"=="" (
    echo [!] Python is not installed or could not be found!
    echo [!] Please install Python from python.org and check "Add python.exe to PATH".
    echo.
    pause
    exit
)

echo [+] Python found at: %PYTHON_EXE%
echo [+] Installing required libraries...
:: Attempt standard pip install first, fallback if no pip module exists
"%PYTHON_EXE%" -m pip install -r requirements.txt --quiet >nul 2>&1
if %errorlevel% neq 0 (
    pip install -r requirements.txt --quiet >nul 2>&1
)

echo.
echo [+] Starting OMAVIY2026 Bot...
start "OMAVIY2026 Bot Run" /Min cmd /c ""%PYTHON_EXE%" bot.py"

echo.
echo ========================================
echo   SUCCESS: Bot is now running in background!
echo   You can stop it anytime using STOP_BOT.bat
echo ========================================
echo.
timeout /t 5
exit
