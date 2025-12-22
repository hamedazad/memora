# Memora Flutter App Setup Script
Write-Host "=== Memora Flutter App Setup ===" -ForegroundColor Green
Write-Host ""

# Check if Flutter is available
$flutterPath = "C:\flutter\bin\flutter.bat"
if (!(Test-Path $flutterPath)) {
    Write-Host "Error: Flutter not found at $flutterPath" -ForegroundColor Red
    Write-Host "Please install Flutter first." -ForegroundColor Red
    Read-Host "Press Enter to continue"
    exit 1
}

Write-Host "Flutter found! Starting setup..." -ForegroundColor Green
Write-Host ""

# Get dependencies
Write-Host "Getting Flutter dependencies..." -ForegroundColor Yellow
try {
    & $flutterPath pub get
    Write-Host "Dependencies installed successfully!" -ForegroundColor Green
} catch {
    Write-Host "Error getting dependencies: $($_.Exception.Message)" -ForegroundColor Red
    Read-Host "Press Enter to continue"
    exit 1
}

Write-Host ""

# Run flutter doctor
Write-Host "Checking Flutter installation..." -ForegroundColor Yellow
try {
    & $flutterPath doctor
} catch {
    Write-Host "Error running flutter doctor: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "=== Setup Complete ===" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Make sure you have Android Studio or VS Code installed" -ForegroundColor White
Write-Host "2. Set up an Android emulator or connect a physical device" -ForegroundColor White
Write-Host "3. Run: flutter run" -ForegroundColor White
Write-Host "4. Or run: flutter run -d chrome (for web development)" -ForegroundColor White
Write-Host ""

Read-Host "Press Enter to continue"


