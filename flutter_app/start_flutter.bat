@echo off
echo === Memora Flutter App Setup ===
echo.

REM Check if Flutter is available
if not exist "C:\flutter\bin\flutter.bat" (
    echo Error: Flutter not found at C:\flutter\bin\flutter.bat
    echo Please install Flutter first.
    pause
    exit /b 1
)

echo Flutter found! Starting setup...
echo.

REM Get dependencies
echo Getting Flutter dependencies...
C:\flutter\bin\flutter.bat pub get
if %errorlevel% neq 0 (
    echo Error getting dependencies
    pause
    exit /b 1
)

echo.
echo Dependencies installed successfully!
echo.

REM Run flutter doctor
echo Checking Flutter installation...
C:\flutter\bin\flutter.bat doctor
echo.

echo === Setup Complete ===
echo.
echo Next steps:
echo 1. Make sure you have Android Studio or VS Code installed
echo 2. Set up an Android emulator or connect a physical device
echo 3. Run: flutter run
echo 4. Or run: flutter run -d chrome (for web development)
echo.

pause


