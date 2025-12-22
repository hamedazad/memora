# Alternative Flutter Download Script
# This script tries multiple methods to download Flutter SDK

Write-Host "=== Alternative Flutter Download Methods ===" -ForegroundColor Green
Write-Host ""

# Flutter download URLs
$flutterUrls = @(
    "https://storage.googleapis.com/flutter_infra_release/releases/stable/windows/flutter_windows_3.16.5-stable.zip",
    "https://github.com/flutter/flutter/releases/download/3.16.5/flutter_windows_3.16.5-stable.zip",
    "https://storage.googleapis.com/flutter_infra_release/releases/stable/windows/flutter_windows_3.16.5-stable.zip"
)

$downloadPath = "C:\flutter.zip"
$extractPath = "C:\"

Write-Host "Trying multiple download methods..." -ForegroundColor Yellow
Write-Host ""

# Method 1: PowerShell with longer timeout
Write-Host "Method 1: PowerShell download..." -ForegroundColor Cyan
try {
    $ProgressPreference = 'SilentlyContinue'
    Invoke-WebRequest -Uri $flutterUrls[0] -OutFile $downloadPath -TimeoutSec 600 -UseBasicParsing
    Write-Host "✓ Download successful with PowerShell!" -ForegroundColor Green
    goto Extract
} catch {
    Write-Host "✗ PowerShell download failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Method 2: Using curl
Write-Host "Method 2: curl download..." -ForegroundColor Cyan
try {
    curl.exe -L -o $downloadPath $flutterUrls[1]
    if (Test-Path $downloadPath) {
        Write-Host "✓ Download successful with curl!" -ForegroundColor Green
        goto Extract
    } else {
        Write-Host "✗ curl download failed" -ForegroundColor Red
    }
} catch {
    Write-Host "✗ curl download failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Method 3: Using .NET WebClient
Write-Host "Method 3: .NET WebClient download..." -ForegroundColor Cyan
try {
    $webClient = New-Object System.Net.WebClient
    $webClient.DownloadFile($flutterUrls[2], $downloadPath)
    Write-Host "✓ Download successful with WebClient!" -ForegroundColor Green
    goto Extract
} catch {
    Write-Host "✗ WebClient download failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Method 4: Try with different timeout
Write-Host "Method 4: PowerShell with different settings..." -ForegroundColor Cyan
try {
    $ProgressPreference = 'SilentlyContinue'
    [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
    Invoke-WebRequest -Uri $flutterUrls[0] -OutFile $downloadPath -TimeoutSec 1200 -UseBasicParsing
    Write-Host "✓ Download successful with modified PowerShell!" -ForegroundColor Green
    goto Extract
} catch {
    Write-Host "✗ Modified PowerShell download failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "All download methods failed. Trying manual alternatives..." -ForegroundColor Red
Write-Host ""
Write-Host "Please try these manual methods:" -ForegroundColor Yellow
Write-Host "1. Download from browser: $($flutterUrls[0])" -ForegroundColor White
Write-Host "2. Use a different network (mobile hotspot)" -ForegroundColor White
Write-Host "3. Try using a VPN" -ForegroundColor White
Write-Host "4. Use Git clone method if you have Git installed" -ForegroundColor White
Write-Host ""
exit 1

:Extract
Write-Host ""
Write-Host "Download successful! Extracting Flutter..." -ForegroundColor Green

# Check if file exists and has content
if (!(Test-Path $downloadPath)) {
    Write-Host "Error: Download file not found!" -ForegroundColor Red
    exit 1
}

$fileSize = (Get-Item $downloadPath).Length
if ($fileSize -lt 1000000) {
    Write-Host "Error: Downloaded file is too small ($fileSize bytes). Download may be incomplete." -ForegroundColor Red
    exit 1
}

Write-Host "File size: $([math]::Round($fileSize/1MB, 2)) MB" -ForegroundColor Cyan

# Extract Flutter
try {
    Write-Host "Extracting to $extractPath..." -ForegroundColor Yellow
    Expand-Archive -Path $downloadPath -DestinationPath $extractPath -Force
    Write-Host "✓ Extraction completed!" -ForegroundColor Green
} catch {
    Write-Host "✗ Extraction failed: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Please extract manually: Extract $downloadPath to C:\" -ForegroundColor Yellow
    exit 1
}

# Clean up
try {
    Remove-Item $downloadPath -Force
    Write-Host "✓ Cleanup completed!" -ForegroundColor Green
} catch {
    Write-Host "Warning: Could not remove download file" -ForegroundColor Yellow
}

# Verify installation
Write-Host ""
Write-Host "Verifying Flutter installation..." -ForegroundColor Yellow
if (Test-Path "C:\flutter\bin\flutter.bat") {
    Write-Host "✓ Flutter installation successful!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Cyan
    Write-Host "1. Add C:\flutter\bin to your PATH" -ForegroundColor White
    Write-Host "2. Restart your terminal" -ForegroundColor White
    Write-Host "3. Run: flutter doctor" -ForegroundColor White
    Write-Host "4. Navigate to your project: cd flutter_app" -ForegroundColor White
    Write-Host "5. Run: flutter pub get" -ForegroundColor White
} else {
    Write-Host "✗ Flutter installation verification failed!" -ForegroundColor Red
    Write-Host "Please check if Flutter was extracted correctly to C:\flutter" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "=== Download and Installation Complete ===" -ForegroundColor Green
















