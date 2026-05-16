@echo off
echo [1/2] Проверка и установка Flask...
pip install flask
echo.
echo [2/2] Запуск сервера YUKSAK ACADEMY...
echo.
echo ========================================================
echo САЙТ: http://localhost:5000
echo АДМИН-ПАНЕЛЬ: http://localhost:5000/admin
echo ЛОГИН: aziz67876578
echo ПАРОЛЬ: 67596854903876584
echo ========================================================
echo.
start http://localhost:5000/admin
python app.py
pause
