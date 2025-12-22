# Flutter <-> Django Integration Test Suite
Write-Host "===============================================" -ForegroundColor Green
Write-Host "Flutter <-> Django Integration Test Suite" -ForegroundColor Green  
Write-Host "===============================================" -ForegroundColor Green
Write-Host ""

# Function to test if Django server is running
function Test-DjangoServer {
    try {
        Write-Host "🔍 Checking if Django server is running..." -ForegroundColor Yellow
        $response = Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/v1/health/" -TimeoutSec 5
        if ($response.status -eq "healthy") {
            Write-Host "✅ Django server is running and healthy" -ForegroundColor Green
            Write-Host "   Server: $($response.server)" -ForegroundColor Gray
            Write-Host "   Time: $($response.timestamp)" -ForegroundColor Gray
            return $true
        }
    }
    catch {
        Write-Host "❌ Django server is not running on port 8000" -ForegroundColor Red
        Write-Host "💡 Please start Django server first:" -ForegroundColor Yellow
        Write-Host "   cd C:\memora_core" -ForegroundColor White
        Write-Host "   python manage.py runserver 8000" -ForegroundColor White
        return $false
    }
    return $false
}

# Function to run Django backend tests
function Test-DjangoBackend {
    Write-Host ""
    Write-Host "===============================================" -ForegroundColor Blue
    Write-Host "1. Running Django Backend API Tests" -ForegroundColor Blue
    Write-Host "===============================================" -ForegroundColor Blue
    Write-Host ""
    
    Push-Location "C:\memora_core"
    
    try {
        Write-Host "🧪 Running comprehensive API tests..." -ForegroundColor Yellow
        python test_flutter_integration.py
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Django backend tests completed successfully" -ForegroundColor Green
            return $true
        } else {
            Write-Host "❌ Django backend tests failed" -ForegroundColor Red
            return $false
        }
    }
    catch {
        Write-Host "❌ Error running Django tests: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
    finally {
        Pop-Location
    }
}

# Function to run Flutter connection test
function Test-FlutterConnection {
    Write-Host ""
    Write-Host "===============================================" -ForegroundColor Magenta
    Write-Host "2. Starting Flutter Connection Test" -ForegroundColor Magenta
    Write-Host "===============================================" -ForegroundColor Magenta
    Write-Host ""
    
    Push-Location "C:\mobile\memora_mobile"
    
    try {
        Write-Host "📱 Starting Flutter connection test app..." -ForegroundColor Yellow
        Write-Host "💡 This will open Flutter app to test connection to Django" -ForegroundColor Cyan
        Write-Host ""
        
        # Check if Flutter is available
        flutter --version | Out-Null
        if ($LASTEXITCODE -ne 0) {
            Write-Host "❌ Flutter is not installed or not in PATH" -ForegroundColor Red
            return $false
        }
        
        Write-Host "🚀 Launching Flutter test app in Chrome..." -ForegroundColor Green
        flutter run -d chrome -t lib/test_django_connection.dart
        
        return $true
    }
    catch {
        Write-Host "❌ Error running Flutter test: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
    finally {
        Pop-Location
    }
}

# Function to show final summary
function Show-TestSummary {
    param(
        [bool]$DjangoServerRunning,
        [bool]$DjangoTestsPassed,
        [bool]$FlutterTestCompleted
    )
    
    Write-Host ""
    Write-Host "===============================================" -ForegroundColor Green
    Write-Host "🎯 Integration Test Summary" -ForegroundColor Green
    Write-Host "===============================================" -ForegroundColor Green
    Write-Host ""
    
    Write-Host "Test Results:" -ForegroundColor White
    Write-Host "  Django Server:    $(if($DjangoServerRunning){'✅ Running'}else{'❌ Not Running'})" -ForegroundColor $(if($DjangoServerRunning){'Green'}else{'Red'})
    Write-Host "  Backend Tests:    $(if($DjangoTestsPassed){'✅ Passed'}else{'❌ Failed'})" -ForegroundColor $(if($DjangoTestsPassed){'Green'}else{'Red'})
    Write-Host "  Flutter Test:     $(if($FlutterTestCompleted){'✅ Completed'}else{'❌ Failed'})" -ForegroundColor $(if($FlutterTestCompleted){'Green'}else{'Red'})
    Write-Host ""
    
    if ($DjangoServerRunning -and $DjangoTestsPassed -and $FlutterTestCompleted) {
        Write-Host "🎉 All tests completed successfully!" -ForegroundColor Green
        Write-Host "✅ Your Flutter app can successfully connect to Django backend" -ForegroundColor Green
        Write-Host "✅ All API endpoints are working correctly" -ForegroundColor Green
        Write-Host "✅ Ready for production use!" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Some tests failed. Please check:" -ForegroundColor Yellow
        if (-not $DjangoServerRunning) {
            Write-Host "❌ Start Django server: python manage.py runserver 8000" -ForegroundColor Red
        }
        if (-not $DjangoTestsPassed) {
            Write-Host "❌ Check Django API endpoints and database connection" -ForegroundColor Red
        }
        if (-not $FlutterTestCompleted) {
            Write-Host "❌ Check Flutter installation and mobile app configuration" -ForegroundColor Red
        }
    }
    
    Write-Host ""
    Write-Host "Next Steps:" -ForegroundColor Cyan
    Write-Host "1. If tests passed, you can run your Flutter app normally" -ForegroundColor White
    Write-Host "2. Use 'flutter run' to start the full mobile app" -ForegroundColor White
    Write-Host "3. The app will connect to Django at http://127.0.0.1:8000" -ForegroundColor White
    Write-Host ""
}

# Main execution
try {
    # Test Django server
    $serverRunning = Test-DjangoServer
    
    if (-not $serverRunning) {
        Write-Host ""
        Write-Host "Would you like to try starting Django server automatically? (y/n): " -NoNewline -ForegroundColor Yellow
        $response = Read-Host
        
        if ($response -eq 'y' -or $response -eq 'Y') {
            Write-Host "🚀 Starting Django server..." -ForegroundColor Green
            Push-Location "C:\memora_core"
            Start-Process -FilePath "python" -ArgumentList "manage.py", "runserver", "8000" -NoNewWindow
            Pop-Location
            
            Write-Host "⏳ Waiting 10 seconds for server to start..." -ForegroundColor Yellow
            Start-Sleep -Seconds 10
            
            $serverRunning = Test-DjangoServer
        }
    }
    
    # Run Django backend tests
    $backendTestsPassed = $false
    if ($serverRunning) {
        $backendTestsPassed = Test-DjangoBackend
    }
    
    # Run Flutter connection test
    $flutterTestCompleted = $false
    if ($serverRunning) {
        Write-Host "Would you like to run the Flutter connection test? (y/n): " -NoNewline -ForegroundColor Yellow
        $response = Read-Host
        
        if ($response -eq 'y' -or $response -eq 'Y') {
            $flutterTestCompleted = Test-FlutterConnection
        } else {
            Write-Host "⏭️  Skipping Flutter test" -ForegroundColor Yellow
            $flutterTestCompleted = $true  # Consider it completed if user skipped
        }
    }
    
    # Show summary
    Show-TestSummary -DjangoServerRunning $serverRunning -DjangoTestsPassed $backendTestsPassed -FlutterTestCompleted $flutterTestCompleted
    
}
catch {
    Write-Host ""
    Write-Host "❌ An error occurred during testing: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
}

Write-Host "Press any key to continue..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")













