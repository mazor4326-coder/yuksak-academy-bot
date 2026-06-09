@echo off
chcp 65001 >nul
title PUBG UC Shop Bot
echo ========================================
echo   🎮 PUBG UC SHOP BOT
echo ========================================
echo.
cd /d "%~dp0"
python pubg_bot.py
pause
