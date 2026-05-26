@echo off
title OMAVIY2026 - ON/OFF Button
cd /d "%~dp0"

:: Check if bot is currently running
set "RUNNING=0"
if exist bot.pid (
    set /p PID=<bot.pid
    tasklist /FI "PID eq %PID%" 2>nul | findstr %PID% >nul
    if %errorlevel% equ 0 (
        set "RUNNING=1"
    )
)

if "%RUNNING%"=="1" (
    echo ========================================
    echo   STATUS: BOT IS RUNNING (PID: %PID%)
    echo   ACTION: STOPPING BOT...
    echo ========================================
    echo.
    taskkill /F /PID %PID% >nul 2>&1
    if exist bot.pid del bot.pid
    echo [OK] OMAVIY2026 Bot has been stopped successfully.
    echo ========================================
    timeout /t 3 >nul
    exit
) else (
    echo ========================================
    echo   STATUS: BOT IS NOT RUNNING
    echo   ACTION: STARTING BOT...
    echo ========================================
    echo.
    
    :: Find python path
    set "PYTHON_EXE="
    if exist "C:\Users\Admin\AppData\Local\Programs\Python\Python311\python.exe" (
        set "PYTHON_EXE=C:\Users\Admin\AppData\Local\Programs\Python\Python311\python.exe"
    ) else (
        python --version >nul 2>&1
        if %errorlevel% equ 0 (
            set "PYTHON_EXE=python"
        ) else if exist "C:\Temp\python_embed\python.exe" (
            set "PYTHON_EXE=C:\Temp\python_embed\python.exe"
        )
    )
    
    if "%PYTHON_EXE%"=="" (
        echo [!] Python is not installed or could not be found!
        echo [!] Please install Python.
        echo.
        pause
        exit
    )
    
    echo [+] Installing required libraries...
    "%PYTHON_EXE%" -m pip install -r requirements.txt --quiet >nul 2>&1
    if %errorlevel% neq 0 (
        pip install -r requirements.txt --quiet >nul 2>&1
    )
    
    echo [+] Starting OMAVIY2026 Bot in background...
    start "OMAVIY2026 Bot Run" /Min cmd /c ""%PYTHON_EXE%" bot.py"
    
    echo [OK] OMAVIY2026 Bot has been started successfully.
    echo ========================================
    timeout /t 3 >nul
    exit
)
