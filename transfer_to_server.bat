@echo off
REM Transfer Memora Core to Ubuntu Server (185.231.59.15)
REM This script prepares and transfers the application to your server

echo 🚀 Preparing Memora Core for transfer to Ubuntu server...

REM Check if .env file exists
if not exist .env (
    echo [WARNING] .env file not found. Creating from production template...
    if exist env.production (
        copy env.production .env
        echo [INFO] Created .env file from production template.
        echo [WARNING] ⚠️  IMPORTANT: Edit .env file with your actual values before transferring!
        echo.
        echo Required changes in .env:
        echo   - SECRET_KEY: Generate a long random string
        echo   - OPENAI_API_KEY: Add your OpenAI API key
        echo   - DB_PASSWORD: Change to a secure password
        echo   - EMAIL_HOST_USER/EMAIL_HOST_PASSWORD: Add if using email
        echo.
        pause
    ) else (
        echo [ERROR] No .env template found. Please create .env file manually.
        exit /b 1
    )
)

REM Get server details
echo [STEP] Enter server connection details:
set /p SERVER_USER="Server username (default: root): "
if "%SERVER_USER%"=="" set SERVER_USER=root

set /p SERVER_IP="Server IP (default: 185.231.59.15): "
if "%SERVER_IP%"=="" set SERVER_IP=185.231.59.15

set /p SERVER_DIR="Server directory (default: /home/%SERVER_USER%): "
if "%SERVER_DIR%"=="" set SERVER_DIR=/home/%SERVER_USER%

REM Create backup of current .env
echo [STEP] Creating backup of .env file...
copy .env .env.backup

REM Create archive using PowerShell
echo [STEP] Creating application archive...
powershell -Command "Compress-Archive -Path '.\*' -DestinationPath 'memora_core.zip' -Force"

if exist memora_core.zip (
    echo [INFO] Archive created: memora_core.zip
) else (
    echo [ERROR] Failed to create archive
    exit /b 1
)

REM Transfer to server
echo [STEP] Transferring to server...
scp memora_core.zip %SERVER_USER%@%SERVER_IP%:%SERVER_DIR%/

if %ERRORLEVEL% EQU 0 (
    echo [INFO] ✅ Transfer completed successfully!
) else (
    echo [ERROR] ❌ Transfer failed!
    exit /b 1
)

REM Create server setup script
echo [STEP] Creating server setup script...
(
echo #!/bin/bash
echo.
echo # Server-side setup script for Memora Core
echo.
echo set -e
echo.
echo echo "🚀 Setting up Memora Core on Ubuntu server..."
echo.
echo # Colors for output
echo GREEN='\033[0;32m'
echo YELLOW='\033[1;33m'
echo BLUE='\033[0;34m'
echo NC='\033[0m'
echo.
echo print_status^(^) {
echo     echo -e "${GREEN}[INFO]${NC} $1"
echo }
echo.
echo print_warning^(^) {
echo     echo -e "${YELLOW}[WARNING]${NC} $1"
echo }
echo.
echo print_step^(^) {
echo     echo -e "${BLUE}[STEP]${NC} $1"
echo }
echo.
echo # Extract files
echo print_step "Extracting application files..."
echo unzip memora_core.zip
echo cd memora_core
echo.
echo # Create .env file
echo print_step "Setting up environment file..."
echo if [ -f env.production ]; then
echo     cp env.production .env
echo     print_warning "⚠️  IMPORTANT: Edit .env file with your actual values!"
echo     echo "Required changes:"
echo     echo "  - SECRET_KEY: Generate a long random string"
echo     echo "  - OPENAI_API_KEY: Add your OpenAI API key"
echo     echo "  - DB_PASSWORD: Change to a secure password"
echo     echo ""
echo     read -p "Press Enter after editing .env file..."
echo else
echo     print_warning "No env.production found. Please create .env file manually."
echo fi
echo.
echo # Make deployment script executable
echo chmod +x deploy-ubuntu.sh
echo.
echo # Run deployment
echo print_step "Starting deployment..."
echo ./deploy-ubuntu.sh
echo.
echo print_status "🎉 Setup completed!"
echo echo ""
echo echo "📋 Next steps:"
echo echo "  1. Change admin password: docker-compose exec web python manage.py changepassword admin"
echo echo "  2. Test application: curl http://%SERVER_IP%/health/"
echo echo "  3. Access admin panel: http://%SERVER_IP%/admin"
echo echo ""
echo echo "🔧 Useful commands:"
echo echo "  - View logs: docker-compose logs -f"
echo echo "  - Check status: docker-compose ps"
echo echo "  - Restart: docker-compose restart"
) > server_setup.sh

REM Transfer setup script
scp server_setup.sh %SERVER_USER%@%SERVER_IP%:%SERVER_DIR%/

echo [INFO] ✅ Server setup script transferred!

REM Final instructions
echo.
echo 🎯 TRANSFER COMPLETED!
echo.
echo 📋 Next steps on your server:
echo   1. SSH into your server:
echo      ssh %SERVER_USER%@%SERVER_IP%
echo.
echo   2. Navigate to the directory:
echo      cd %SERVER_DIR%
echo.
echo   3. Run the setup script:
echo      chmod +x server_setup.sh
echo      ./server_setup.sh
echo.
echo   4. Follow the prompts to complete deployment
echo.
echo 🔗 Application will be available at:
echo    - Main app: http://%SERVER_IP%
echo    - Admin panel: http://%SERVER_IP%/admin
echo    - Default admin: admin/admin123 ^(change immediately!^)
echo.
echo [WARNING] ⚠️  Remember to edit .env file with your actual values before running setup!

pause
