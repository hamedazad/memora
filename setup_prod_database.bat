@echo off
REM Production Database Setup (PostgreSQL)
echo ========================================
echo Production Database Setup (PostgreSQL)
echo ========================================
echo.

REM Check environment variables
if "%DB_NAME%"=="" (
    echo ERROR: DB_NAME not set
    goto :missing_vars
)
if "%DB_USER%"=="" (
    echo ERROR: DB_USER not set
    goto :missing_vars
)
if "%DB_PASSWORD%"=="" (
    echo ERROR: DB_PASSWORD not set
    goto :missing_vars
)
if "%DB_HOST%"=="" (
    echo ERROR: DB_HOST not set
    goto :missing_vars
)

echo Configuration:
echo   Host: %DB_HOST%
echo   Database: %DB_NAME%
echo   User: %DB_USER%
echo.

REM Set environment
set ENVIRONMENT=production
set DB_ENGINE=django.db.backends.postgresql

echo Testing database connection...
python manage.py dbshell --command "SELECT version();" >nul 2>&1
if errorlevel 1 (
    echo ERROR: Cannot connect to PostgreSQL
    echo.
    echo Check:
    echo   1. PostgreSQL is running
    echo   2. Database exists: createdb %DB_NAME%
    echo   3. User has permissions
    echo.
    pause
    exit /b 1
)

echo   Connection successful!
echo.

echo Running migrations...
python manage.py migrate

echo.
echo Collecting static files...
python manage.py collectstatic --noinput

echo.
echo ========================================
echo Production database setup complete!
echo ========================================
echo.
echo Next steps:
echo   1. Create admin: python manage.py createsuperuser
echo   2. Test application
echo   3. Configure production web server
echo.
pause
exit /b 0

:missing_vars
echo.
echo Please set these environment variables:
echo   set DB_NAME=memora_db
echo   set DB_USER=memora_user
echo   set DB_PASSWORD=your_password
echo   set DB_HOST=localhost
echo   set DB_PORT=5432
echo.
echo Or create .env file with these values
echo.
pause
exit /b 1




























