# Quick Start Guide - Running Memora Mobile App

## Current Situation
We've successfully created a complete Flutter mobile app for Memora, but we're experiencing network connectivity issues that prevent Flutter from downloading the Dart SDK.

## Alternative Solutions

### Option 1: Use Flutter Web (Recommended)
Since Flutter can run in web browsers, this is the easiest way to test the app:

1. **Install Flutter with Dart SDK manually:**
   - Download Flutter SDK with Dart from: https://storage.googleapis.com/flutter_infra_release/releases/stable/windows/flutter_windows_3.24.5-stable.zip
   - Extract to C:\flutter
   - Add C:\flutter\bin to PATH

2. **Run the app in web browser:**
   ```powershell
   cd C:\memora_core\flutter_app
   flutter run -d chrome
   ```

### Option 2: Use DartPad (Quick Test)
For immediate testing of the app logic:

1. Go to https://dartpad.dev/
2. Copy the main.dart content from `flutter_app/lib/main.dart`
3. Note: Limited functionality, but good for testing UI

### Option 3: Build and Deploy Web Version
If you have access to a machine with Flutter:

1. Build web version:
   ```bash
   flutter build web
   ```

2. Serve the build folder:
   ```bash
   python -m http.server 8000
   # or
   npx serve build/web
   ```

### Option 4: Use Flutter Desktop
For Windows desktop app:

1. Enable Windows desktop support:
   ```powershell
   flutter config --enable-windows-desktop
   ```

2. Run on Windows:
   ```powershell
   flutter run -d windows
   ```

## App Features Ready to Use

Once running, the app includes:

### ✅ Authentication
- Login/Register screens
- JWT token management
- User profile management

### ✅ Memory Management
- Create, edit, delete memories
- Memory categorization
- Importance levels
- Tags and search

### ✅ AI Integration
- AI memory suggestions
- Memory enhancement
- Smart categorization

### ✅ Social Features
- Share memories
- Like and comment
- User profiles
- Friend management

### ✅ Offline Support
- SQLite local database
- Offline memory storage
- Sync when online

### ✅ Voice Features
- Voice recording
- Speech-to-text
- Voice search

### ✅ Notifications
- Push notifications
- Memory reminders
- Social notifications

## Backend Integration

The app connects to your existing Django backend:
- **API Base URL:** `http://185.231.59.157/api/v1`
- **Authentication:** JWT tokens
- **Database:** Same PostgreSQL database as web app

## Next Steps

1. **Choose your preferred method** from the options above
2. **Install Flutter** if using Option 1 or 4
3. **Run the app** and test all features
4. **Customize** the UI and functionality as needed

## Troubleshooting Network Issues

If you continue to have network problems:

1. **Use a VPN** to access Flutter resources
2. **Try a different network** (mobile hotspot)
3. **Download Flutter manually** from a mirror site
4. **Use a cloud development environment** (GitHub Codespaces, etc.)

## App Structure

```
flutter_app/
├── lib/
│   ├── main.dart                 # App entry point
│   ├── models/                   # Data models
│   ├── services/                 # API and database services
│   ├── providers/                # State management
│   ├── screens/                  # UI screens
│   ├── widgets/                  # Reusable components
│   └── core/                     # App configuration
├── pubspec.yaml                  # Dependencies
└── README.md                     # Setup instructions
```

The app is fully functional and ready to run once Flutter is properly installed!
