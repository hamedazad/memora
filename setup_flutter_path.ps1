# Flutter PATH Setup Script
# This script adds Flutter to your PATH and verifies the installation

Write-Host "=== Flutter PATH Setup ===" -ForegroundColor Green

# Flutter directory
$flutterDir = "C:\flutter"
$flutterBinPath = "$flutterDir\bin"

# Check if Flutter directory exists
if (!(Test-Path $flutterDir)) {
    Write-Host "Error: Flutter directory not found at $flutterDir" -ForegroundColor Red
    Write-Host "Please make sure Flutter is installed correctly." -ForegroundColor Red
    exit 1
}

Write-Host "Flutter found at: $flutterDir" -ForegroundColor Green

# Check if bin directory exists
if (!(Test-Path $flutterBinPath)) {
    Write-Host "Error: Flutter bin directory not found at $flutterBinPath" -ForegroundColor Red
    exit 1
}

Write-Host "Flutter bin directory found at: $flutterBinPath" -ForegroundColor Green

# Add Flutter to PATH
Write-Host "Adding Flutter to PATH..." -ForegroundColor Yellow

# Get current user PATH
$currentPath = [Environment]::GetEnvironmentVariable("PATH", "User")

# Check if Flutter is already in PATH
if ($currentPath -like "*$flutterBinPath*") {
    Write-Host "Flutter is already in PATH!" -ForegroundColor Green
} else {
    # Add Flutter to PATH
    $newPath = "$currentPath;$flutterBinPath"
    [Environment]::SetEnvironmentVariable("PATH", $newPath, "User")
    Write-Host "Flutter added to PATH successfully!" -ForegroundColor Green
}

# Update current session PATH
$env:PATH = [Environment]::GetEnvironmentVariable("PATH", "User") + ";" + [Environment]::GetEnvironmentVariable("PATH", "Machine")

# Test Flutter installation
Write-Host "`nTesting Flutter installation..." -ForegroundColor Yellow

try {
    $flutterVersion = & "$flutterBinPath\flutter.bat" --version
    Write-Host "Flutter installation successful!" -ForegroundColor Green
    Write-Host "Version info:" -ForegroundColor Cyan
    Write-Host $flutterVersion -ForegroundColor White
} catch {
    Write-Host "Error testing Flutter installation: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Please restart your terminal and try again." -ForegroundColor Yellow
}

# Run flutter doctor
Write-Host "`nRunning flutter doctor..." -ForegroundColor Yellow
try {
    & "$flutterBinPath\flutter.bat" doctor
} catch {
    Write-Host "Error running flutter doctor: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n=== Setup Complete ===" -ForegroundColor Green
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Restart your terminal/PowerShell to ensure PATH changes take effect" -ForegroundColor White
Write-Host "2. Navigate to your Flutter project: cd flutter_app" -ForegroundColor White
Write-Host "3. Run: flutter pub get" -ForegroundColor White
Write-Host "4. Run: flutter doctor to check for any missing dependencies" -ForegroundColor White
Write-Host "5. Run: flutter run to start your app" -ForegroundColor White

Write-Host "`nIf you see any issues with flutter doctor, please install the missing dependencies." -ForegroundColor Yellow
















