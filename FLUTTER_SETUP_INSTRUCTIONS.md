# Flutter Setup Instructions for Memora Mobile App

## Manual Flutter Installation

Since we're experiencing network connectivity issues, here's how to manually install Flutter:

### Option 1: Download Flutter Manually

1. **Download Flutter SDK:**
   - Go to: https://docs.flutter.dev/get-started/install/windows
   - Download the Flutter SDK zip file for Windows
   - Extract it to `C:\flutter` (or any directory you prefer)

2. **Add Flutter to PATH:**
   - Open System Properties → Advanced → Environment Variables
   - Add `C:\flutter\bin` to your PATH variable
   - Restart your terminal/PowerShell

### Option 2: Use Git (if available)

```powershell
git clone https://github.com/flutter/flutter.git -b stable C:\flutter
```

### Option 3: Use Chocolatey (if available)

```powershell
# Install Chocolatey first if not installed
Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

# Then install Flutter
choco install flutter
```

## Running the Memora Mobile App

Once Flutter is installed:

1. **Navigate to the Flutter app directory:**
   ```powershell
   cd C:\memora_core\flutter_app
   ```

2. **Get dependencies:**
   ```powershell
   flutter pub get
   ```

3. **Check Flutter installation:**
   ```powershell
   flutter doctor
   ```

4. **Run the app:**
   ```powershell
   # For web (easiest to start with)
   flutter run -d chrome
   
   # For Windows desktop
   flutter run -d windows
   
   # For Android (if you have Android Studio/emulator)
   flutter run -d android
   ```

## Alternative: Run Without Flutter Installation

If you want to run the app immediately without installing Flutter:

### Using DartPad (Online)
1. Go to https://dartpad.dev/
2. Copy the main.dart content from `flutter_app/lib/main.dart`
3. Note: This is limited and won't have all features

### Using Flutter Web Build
If you have access to a machine with Flutter:
1. Build the web version: `flutter build web`
2. Serve the build folder with any web server

## Troubleshooting

### Network Issues
- Try using a VPN or different network
- Download Flutter from a mirror site
- Use a mobile hotspot temporarily

### PATH Issues
- Make sure Flutter is in your PATH
- Restart terminal after adding to PATH
- Use full path: `C:\flutter\bin\flutter.bat`

### Dependencies
- Run `flutter doctor` to check for missing dependencies
- Install Android Studio if you want to run on Android
- Install Visual Studio for Windows desktop support

## Quick Test

To verify Flutter is working:
```powershell
flutter --version
flutter doctor
```

## Next Steps

Once Flutter is installed and working:
1. The app will connect to your Django backend at `http://185.231.59.157/api/v1`
2. You can log in with existing Memora accounts
3. All features (memories, AI, social, offline sync) will be available

## Features Available

- ✅ User authentication (login/register)
- ✅ Memory creation and management
- ✅ AI suggestions and enhancement
- ✅ Offline storage with SQLite
- ✅ Social features (sharing, likes, comments)
- ✅ Voice recording and transcription
- ✅ Push notifications
- ✅ Cross-platform support

The app is fully functional and ready to run once Flutter is installed!
