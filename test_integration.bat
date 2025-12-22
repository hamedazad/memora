@echo off
echo ===============================================
echo Flutter ^<-^> Django Integration Test Suite
echo ===============================================
echo.

:: Check if Django server is running
echo 🔍 Checking if Django server is running...
curl -s -f http://127.0.0.1:8000/api/v1/health/ >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Django server is not running on port 8000
    echo 💡 Please start Django server first: python manage.py runserver 8000
    echo.
    echo Starting Django server...
    cd C:\memora_core
    start cmd /k "python manage.py runserver 8000"
    echo ⏳ Waiting 10 seconds for server to start...
    timeout /t 10 /nobreak >nul
) else (
    echo ✅ Django server is running
)

echo.
echo ===============================================
echo 1. Running Django Backend API Tests
echo ===============================================
echo.

cd C:\memora_core
python test_flutter_integration.py

echo.
echo ===============================================
echo 2. Starting Flutter Connection Test
echo ===============================================
echo.

cd C:\mobile\memora_mobile
echo 📱 Starting Flutter connection test app...
echo 💡 This will open Flutter app to test connection to Django
echo.

:: Run Flutter test app
flutter run -d chrome -t lib/test_django_connection.dart

echo.
echo ===============================================
echo 🎯 Integration Test Complete
echo ===============================================
echo.
echo If both tests passed:
echo ✅ Your Flutter app can successfully connect to Django backend
echo ✅ All API endpoints are working correctly
echo ✅ Ready for production use!
echo.
echo If any tests failed:
echo ❌ Check Django server is running on port 8000
echo ❌ Verify all API endpoints are configured correctly
echo ❌ Check CORS settings allow Flutter app connections
echo.
pause













