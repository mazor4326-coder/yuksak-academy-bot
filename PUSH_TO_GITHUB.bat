@echo off
title GitHub'ga yuklash - Yuksak Academy
echo ========================================
echo   LOYIHANI GITHUB'GA YUKLASH SKRIPTI
echo ========================================
echo.

:: Git borligini tekshirish
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] Git o'rnatilmagan!
    echo [!] Hozir Git o'rnatish fayli yuklanadi...
    echo.
    
    :: Gitni curl orqali yuklash (Windows 10+ da curl bor)
    curl -L https://github.com/git-for-windows/git/releases/download/v2.45.0.windows.1/Git-2.45.0-64-bit.exe -o git_installer.exe
    
    echo [!] Yuklab olindi. O'rnatish boshlanmoqda...
    echo [!] O'rnatish oynasida faqat "Next" va "Finish" tugmalarini bosing.
    
    :: O'rnatuvchini ishga tushirish va kutish
    start /wait git_installer.exe
    
    echo.
    echo [OK] Git o'rnatildi! 
    echo [!] DIQQAT: O'zgarishlar kuchga kirishi uchun ushbu oynani yopib,
    echo     skriptni qaytadan ishga tushiring.
    del git_installer.exe
    pause
    exit
)

:: Agar Git bo'lsa, yuklashni boshlash
echo [+] Git aniqlandi. Yuklash davom etadi...
echo.

set /p repo_url="GitHub Repozitoriya linkini kiriting: "
set /p token="GitHub Tokeningizni kiriting: "

if not exist .git (
    git init
)

git add .
git commit -m "Initial commit"
git branch -M main

git remote remove origin >nul 2>&1
set "clean_url=%repo_url:https://=%"
git remote add origin https://%token%@%clean_url%

echo.
echo GitHub'ga yuklanmoqda...
git push -u origin main

echo.
echo ========================================
echo   TAYYOR! Loyiha GitHub'ga yuklandi.
echo ========================================
pause
