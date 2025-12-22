@echo off
echo ========================================
echo Restarting Django Server
echo ========================================
echo.

REM Kill any existing Django processes
echo Stopping existing Django processes...
taskkill /F /IM python.exe /FI "WINDOWTITLE eq *manage.py*" 2>nul
timeout /t 2 /nobreak >nul

echo.
echo Starting Django development server...
echo Server will be available at http://127.0.0.1:8000
echo.

REM Start Django server
python manage.py runserver 0.0.0.0:8000

pause
























