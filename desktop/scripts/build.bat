@echo off
REM Build script for The Lariat Bible Desktop App (Windows)

echo ==========================================
echo Building The Lariat Bible Desktop App
echo ==========================================

set SCRIPT_DIR=%~dp0
set DESKTOP_DIR=%SCRIPT_DIR%..
set PROJECT_DIR=%DESKTOP_DIR%\..

cd /d %PROJECT_DIR%

REM Step 1: Install Python dependencies
echo.
echo [1/5] Installing Python dependencies...
pip install -r requirements.txt --quiet

REM Step 2: Build React frontend
echo.
echo [2/5] Building React frontend...
cd frontend
call npm install --silent
call npm run build
cd ..

REM Step 3: Copy frontend build to desktop app
echo.
echo [3/5] Copying frontend build...
if exist desktop\app rmdir /s /q desktop\app
xcopy /s /e /i frontend\dist desktop\app

REM Step 4: Install Electron dependencies
echo.
echo [4/5] Installing Electron dependencies...
cd desktop
call npm install --silent

REM Step 5: Build desktop app
echo.
echo [5/5] Building desktop installer...
call npm run build:win

echo.
echo ==========================================
echo Build complete!
echo ==========================================
echo.
echo Installers are in: desktop\dist\
dir dist\*.exe 2>nul

pause
