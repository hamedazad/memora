@echo off
echo ========================================
echo Fixing Duplicate UserProfile Model
echo ========================================
echo.

echo Step 1: Checking for existing migrations...
python manage.py showmigrations memory_assistant
echo.

echo Step 2: Creating new migration for UserProfile changes...
python manage.py makemigrations memory_assistant --name merge_duplicate_userprofile
echo.

echo Step 3: Reviewing migration SQL (press Ctrl+C to cancel)...
pause
python manage.py sqlmigrate memory_assistant 0026
echo.

echo Step 4: Running migration (press Ctrl+C to cancel)...
pause
python manage.py migrate memory_assistant
echo.

echo Step 5: Verifying model integrity...
python manage.py check
echo.

echo ========================================
echo Migration Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Test user registration and profile creation
echo 2. Verify existing profiles still work
echo 3. Check mobile app integration
echo.
echo Documentation: DUPLICATE_USERPROFILE_FIX.md
echo.
pause






























