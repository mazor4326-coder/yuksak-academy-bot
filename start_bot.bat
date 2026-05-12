@echo off
chcp 65001 >nul
echo Установка необходимых библиотек...
pip install -r requirements.txt
echo.
echo ========================================
echo Запуск Telegram Bot...
echo ========================================
python bot.py
pause
