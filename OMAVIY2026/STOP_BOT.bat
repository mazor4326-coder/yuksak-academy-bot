@echo off
title OMAVIY2026 Bot Stopper
cd /d "%~dp0"
echo ========================================
echo   STOPPING OMAVIY2026 AD-POSTING BOT
echo ========================================
echo.

if not exist bot.pid (
    echo [!] No active bot PID file found.
    echo [!] It seems the bot is not running.
    echo.
    pause
    exit
)

set /p PID=<bot.pid

echo [+] Terminating Bot process (PID: %PID%)...
taskkill /F /PID %PID% >nul 2>&1

if %errorlevel% equ 0 (
    echo [OK] Bot process killed successfully.
) else (
    echo [!] Could not terminate process. It might have already exited.
)

:: Clean up PID file
if exist bot.pid del bot.pid

echo.
echo ========================================
echo   SUCCESS: OMAVIY2026 Bot has been stopped.
echo ========================================
echo.
timeout /t 5
exit
