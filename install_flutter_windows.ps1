# Flutter Installation Script for Windows
# This script downloads Flutter SDK manually and sets up the environment

Write-Host "=== Flutter SDK Installation Script ===" -ForegroundColor Green

# Create Flutter directory
$flutterDir = "C:\flutter"
Write-Host "Creating Flutter directory at: $flutterDir" -ForegroundColor Yellow

if (!(Test-Path $flutterDir)) {
    New-Item -ItemType Directory -Path $flutterDir -Force
}

# Download Flutter SDK
Write-Host "Downloading Flutter SDK..." -ForegroundColor Yellow

# Flutter SDK download URLs (choose one based on your preference)
$flutterUrls = @{
    "stable" = "https://storage.googleapis.com/flutter_infra_release/releases/stable/windows/flutter_windows_3.16.5-stable.zip"
    "beta" = "https://storage.googleapis.com/flutter_infra_release/releases/beta/windows/flutter_windows_3.16.5-beta.zip"
    "dev" = "https://storage.googleapis.com/flutter_infra_release/releases/dev/windows/flutter_windows_3.16.5-dev.zip"
}

Write-Host "Available Flutter versions:" -ForegroundColor Cyan
Write-Host "1. Stable (Recommended): $($flutterUrls['stable'])" -ForegroundColor White
Write-Host "2. Beta: $($flutterUrls['beta'])" -ForegroundColor White
Write-Host "3. Dev: $($flutterUrls['dev'])" -ForegroundColor White

$choice = Read-Host "Enter your choice (1-3) [Default: 1]"
if ($choice -eq "" -or $choice -eq "1") {
    $flutterUrl = $flutterUrls["stable"]
    $version = "stable"
} elseif ($choice -eq "2") {
    $flutterUrl = $flutterUrls["beta"]
    $version = "beta"
} elseif ($choice -eq "3") {
    $flutterUrl = $flutterUrls["dev"]
    $version = "dev"
} else {
    Write-Host "Invalid choice. Using stable version." -ForegroundColor Yellow
    $flutterUrl = $flutterUrls["stable"]
    $version = "stable"
}

$zipFile = "$flutterDir\flutter.zip"
Write-Host "Downloading Flutter $version from: $flutterUrl" -ForegroundColor Yellow

try {
    # Download using PowerShell
    Invoke-WebRequest -Uri $flutterUrl -OutFile $zipFile -UseBasicParsing
    Write-Host "Download completed successfully!" -ForegroundColor Green
} catch {
    Write-Host "Download failed. Trying alternative method..." -ForegroundColor Red
    
    # Alternative download method using curl
    try {
        curl.exe -L -o $zipFile $flutterUrl
        Write-Host "Download completed using curl!" -ForegroundColor Green
    } catch {
        Write-Host "Both download methods failed. Please download manually:" -ForegroundColor Red
        Write-Host "1. Visit: https://docs.flutter.dev/get-started/install/windows" -ForegroundColor Cyan
        Write-Host "2. Download the Flutter SDK zip file" -ForegroundColor Cyan
        Write-Host "3. Extract to: $flutterDir" -ForegroundColor Cyan
        exit 1
    }
}

# Extract Flutter SDK
Write-Host "Extracting Flutter SDK..." -ForegroundColor Yellow
try {
    Expand-Archive -Path $zipFile -DestinationPath "C:\" -Force
    Write-Host "Extraction completed!" -ForegroundColor Green
} catch {
    Write-Host "Extraction failed. Please extract manually:" -ForegroundColor Red
    Write-Host "1. Extract $zipFile to C:\" -ForegroundColor Cyan
    Write-Host "2. Ensure Flutter is in C:\flutter" -ForegroundColor Cyan
    exit 1
}

# Clean up zip file
Remove-Item $zipFile -Force

# Add Flutter to PATH
Write-Host "Adding Flutter to PATH..." -ForegroundColor Yellow
$flutterBinPath = "$flutterDir\bin"

# Check if Flutter is already in PATH
$currentPath = [Environment]::GetEnvironmentVariable("PATH", "User")
if ($currentPath -notlike "*$flutterBinPath*") {
    $newPath = "$currentPath;$flutterBinPath"
    [Environment]::SetEnvironmentVariable("PATH", $newPath, "User")
    Write-Host "Flutter added to PATH!" -ForegroundColor Green
} else {
    Write-Host "Flutter already in PATH!" -ForegroundColor Green
}

# Verify installation
Write-Host "Verifying Flutter installation..." -ForegroundColor Yellow
$env:PATH = [Environment]::GetEnvironmentVariable("PATH", "User") + ";" + [Environment]::GetEnvironmentVariable("PATH", "Machine")

try {
    & "$flutterBinPath\flutter.bat" --version
    Write-Host "Flutter installation successful!" -ForegroundColor Green
} catch {
    Write-Host "Flutter verification failed. Please restart your terminal and try again." -ForegroundColor Red
}

Write-Host "`n=== Next Steps ===" -ForegroundColor Green
Write-Host "1. Restart your terminal/PowerShell" -ForegroundColor Cyan
Write-Host "2. Run: flutter doctor" -ForegroundColor Cyan
Write-Host "3. Install any missing dependencies" -ForegroundColor Cyan
Write-Host "4. Navigate to your project: cd flutter_app" -ForegroundColor Cyan
Write-Host "5. Run: flutter pub get" -ForegroundColor Cyan

Write-Host "`nInstallation script completed!" -ForegroundColor Green
















