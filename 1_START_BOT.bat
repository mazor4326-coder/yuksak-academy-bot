@echo off
title YUKSAK ACADEMY BOT
color 0A
echo ===================================================
echo         YUKSAK ACADEMY BOT ISHGA TUSHYAPTI...
echo ===================================================
echo.
echo Botni to'xtatish uchun ushbu oynani yoping.
echo.
set "PYTHON_EXE="
if exist "C:\Users\Admin\AppData\Local\Programs\Python\Python311\python.exe" (
    set "PYTHON_EXE=C:\Users\Admin\AppData\Local\Programs\Python\Python311\python.exe"
) else if exist "C:\Temp\python_embed\python.exe" (
    set "PYTHON_EXE=C:\Temp\python_embed\python.exe"
) else (
    set "PYTHON_EXE=python"
)

"%PYTHON_EXE%" -m pip install -r requirements.txt --quiet >nul 2>&1
"%PYTHON_EXE%" bot.py
pause
