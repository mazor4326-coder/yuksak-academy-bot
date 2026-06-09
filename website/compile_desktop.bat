@echo off
title YUKSAK ACADEMY - Compiler Command Line
echo [INFO] Installing required compilation dependencies...
pip install pywebview pyinstaller flask requests

echo [INFO] Cleaning up previous build configurations...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist Yuksak_Academy.spec del Yuksak_Academy.spec

echo [INFO] Initiating PyInstaller compilation process...
echo [INFO] Packaging all templates, stylesheets, scripts and digital assets...
pyinstaller --onefile --noconsole --name="Yuksak_Academy" --add-data "index.html;." --add-data "style.css;." --add-data "main.js;." --add-data "templates;templates" --add-data "assets;assets" desktop_app.py

echo [INFO] Verification: checking output executable...
if exist dist\Yuksak_Academy.exe (
    copy /y dist\Yuksak_Academy.exe Yuksak_Academy.exe >nul
    echo ==============================================================
    echo [SUCCESS] Standalone EXE compiled successfully!
    echo [PATH] c:\Users\Admin\Music\образование\website\Yuksak_Academy.exe
    echo ==============================================================
) else (
    echo [ERROR] Compilation failed. Please inspect build output above.
)
pause
