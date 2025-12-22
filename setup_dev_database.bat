@echo off
REM Development Database Setup (SQLite)
echo ========================================
echo Development Database Setup (SQLite)
echo ========================================
echo.

REM Set environment
set ENVIRONMENT=development
set DB_ENGINE=django.db.backends.sqlite3

echo Current configuration:
echo   Environment: %ENVIRONMENT%
echo   Database: SQLite (db.sqlite3)
echo.

REM Ask about resetting database
set /p RESET="Reset database? This will DELETE all data! (y/N): "
if /i "%RESET%"=="y" (
    if exist db.sqlite3 (
        del db.sqlite3
        echo   Removed old database
    )
)

echo.
echo Running migrations...
python manage.py migrate

echo.
echo ========================================
echo Database setup complete!
echo ========================================
echo.
echo Database file: db.sqlite3
echo.
echo Next steps:
echo   1. Create admin user: python manage.py createsuperuser
echo   2. Start server: python manage.py runserver
echo   3. Access admin: http://localhost:8000/admin/
echo.
pause




























