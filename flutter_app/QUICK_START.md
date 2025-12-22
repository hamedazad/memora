# Quick Start Guide - Memora Flutter App

## ✅ Flutter Installation Complete!

Your Flutter SDK is now installed at `C:\flutter` and ready to use.

## 🚀 Getting Started

### Option 1: Use the Setup Script (Recommended)
```powershell
# Run the PowerShell setup script
.\start_flutter.ps1
```

### Option 2: Manual Setup
```powershell
# Navigate to the Flutter app directory
cd flutter_app

# Get dependencies
C:\flutter\bin\flutter.bat pub get

# Check Flutter installation
C:\flutter\bin\flutter.bat doctor
```

## 📱 Running the App

### For Android Development:
1. Install Android Studio
2. Set up an Android emulator or connect a physical device
3. Run: `C:\flutter\bin\flutter.bat run`

### For Web Development:
```powershell
C:\flutter\bin\flutter.bat run -d chrome
```

### For Windows Desktop:
```powershell
C:\flutter\bin\flutter.bat run -d windows
```

## 🔧 Development Tools

### Recommended IDEs:
- **VS Code** with Flutter extension
- **Android Studio** with Flutter plugin
- **IntelliJ IDEA** with Flutter plugin

### VS Code Setup:
1. Install VS Code
2. Install Flutter extension
3. Open the `flutter_app` folder
4. Press F5 to run the app

## 📋 Project Structure

```
flutter_app/
├── lib/
│   ├── main.dart              # App entry point
│   ├── screens/               # UI screens
│   ├── widgets/               # Reusable components
│   ├── services/              # API and business logic
│   ├── providers/             # State management
│   ├── models/                # Data models
│   └── core/                  # Core utilities
├── pubspec.yaml              # Dependencies
└── README.md                 # Project documentation
```

## 🔗 Backend Integration

The app connects to your Django backend at:
- **Base URL**: `http://185.231.59.157/api/v1`
- **Authentication**: JWT tokens
- **Database**: PostgreSQL (same as web app)

## 🛠️ Common Commands

```powershell
# Get dependencies
C:\flutter\bin\flutter.bat pub get

# Run the app
C:\flutter\bin\flutter.bat run

# Build for release
C:\flutter\bin\flutter.bat build apk --release

# Check Flutter installation
C:\flutter\bin\flutter.bat doctor

# Clean and rebuild
C:\flutter\bin\flutter.bat clean
C:\flutter\bin\flutter.bat pub get
```

## 🐛 Troubleshooting

### Flutter not found:
- Make sure Flutter is in `C:\flutter`
- Add `C:\flutter\bin` to your PATH
- Restart your terminal

### Dependencies issues:
```powershell
C:\flutter\bin\flutter.bat clean
C:\flutter\bin\flutter.bat pub get
```

### Build issues:
- Check `flutter doctor` output
- Install missing dependencies
- Update Flutter SDK if needed

## 📞 Support

If you encounter issues:
1. Check the Flutter documentation: https://docs.flutter.dev/
2. Run `flutter doctor` to identify problems
3. Check the project README.md for detailed information

## 🎉 Next Steps

1. ✅ Flutter SDK installed
2. 🔄 Run the setup script
3. 📱 Set up development environment
4. 🚀 Start developing your Memora mobile app!

---

**Happy coding! 🎨📱**


