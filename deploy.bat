@echo off
REM Memora Core Deployment Script for Windows
REM This script prepares the deployment on Windows before uploading to server

echo 🚀 Preparing Memora Core for Deployment...

REM Check if .env file exists
if not exist .env (
    echo [WARNING] .env file not found. Creating from template...
    if exist env.production.example (
        copy env.production.example .env
        echo [INFO] Created .env file from template. Please edit it with your production values.
        echo [WARNING] You need to edit .env file before continuing!
        pause
        exit /b 1
    ) else (
        echo [ERROR] No .env template found. Please create .env file manually.
        pause
        exit /b 1
    )
)

REM Create necessary directories
echo [INFO] Creating necessary directories...
if not exist docker\nginx\ssl mkdir docker\nginx\ssl
if not exist logs mkdir logs
if not exist media mkdir media
if not exist staticfiles mkdir staticfiles

echo [INFO] Preparation completed!
echo.
echo 📋 Next Steps:
echo   1. Edit .env file with your production values
echo   2. Upload all files to your server using FileZilla
echo   3. SSH into your server and run: ./deploy.sh
echo.
echo 📁 Files to upload:
echo   - All project files and folders
echo   - Dockerfile
echo   - docker-compose.yml
echo   - requirements.txt
echo   - requirements_production.txt
echo   - .env (your production environment file)
echo   - docker/ folder
echo   - deploy.sh
echo.
echo 📖 For detailed instructions, see DEPLOYMENT.md
pause
