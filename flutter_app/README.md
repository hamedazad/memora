# Memora Flutter App

A complete Flutter mobile application for the Memora memory management system.

## Features

- ✅ **Authentication**: Login/Register with JWT tokens
- ✅ **Memory Management**: Create, read, update, delete memories
- ✅ **Offline Support**: Local SQLite database with sync
- ✅ **AI Integration**: Memory suggestions and enhancements
- ✅ **Voice Features**: Voice recording and transcription
- ✅ **Social Features**: Likes, comments, and sharing
- ✅ **Smart Reminders**: Scheduled notifications
- ✅ **Cross-platform**: iOS and Android support

## Backend Integration

This app connects to your existing Django Memora backend at:
- **Base URL**: `http://185.231.59.157/api/v1`
- **Authentication**: JWT tokens
- **Database**: Uses same PostgreSQL database as web app

## Prerequisites

1. **Flutter SDK** (3.10.0 or higher)
2. **Dart SDK** (3.0.0 or higher)
3. **Android Studio** (for Android development)
4. **Xcode** (for iOS development - macOS only)

## Quick Start

### 1. Install Flutter

Follow the official Flutter installation guide:
https://docs.flutter.dev/get-started/install

### 2. Clone and Setup

```bash
# Navigate to the flutter app directory
cd flutter_app

# Get dependencies
flutter pub get

# Run code generation (if needed)
flutter packages pub run build_runner build
```

### 3. Run the App

#### Option A: Using Flutter Command Line

```bash
# Run on connected device/emulator
flutter run

# Run on specific device
flutter devices  # List available devices
flutter run -d <device-id>

# Run in debug mode
flutter run --debug

# Run in release mode
flutter run --release
```

#### Option B: Using VS Code

1. Install Flutter and Dart extensions
2. Open the project in VS Code
3. Press F5 or use "Run and Debug"

#### Option C: Using Android Studio

1. Open the project in Android Studio
2. Select device/emulator
3. Click the Run button

### 4. Build for Production

#### Android APK

```bash
flutter build apk --release
```

#### Android App Bundle (for Play Store)

```bash
flutter build appbundle --release
```

#### iOS (macOS only)

```bash
flutter build ios --release
```

## Project Structure

```
flutter_app/
├── lib/
│   ├── main.dart                 # App entry point
│   ├── core/                     # Core utilities
│   │   ├── app_theme.dart        # Theme configuration
│   │   └── router.dart           # Navigation setup
│   ├── models/                   # Data models
│   │   ├── memory.dart           # Memory model
│   │   ├── user.dart             # User model
│   │   └── ai_models.dart        # AI-related models
│   ├── services/                 # Business logic
│   │   ├── api_service.dart      # Backend API integration
│   │   ├── database_service.dart # Local database
│   │   └── notification_service.dart # Push notifications
│   ├── providers/                # State management
│   │   ├── auth_provider.dart    # Authentication state
│   │   └── memory_provider.dart  # Memory state
│   ├── screens/                  # UI screens
│   │   ├── auth/                 # Login/Register
│   │   ├── home/                 # Dashboard
│   │   ├── memories/             # Memory management
│   │   ├── profile/              # User profile
│   │   ├── search/               # Search functionality
│   │   └── ai/                   # AI features
│   └── widgets/                  # Reusable components
│       ├── memory_card.dart      # Memory display card
│       ├── dashboard_stats_card.dart # Stats display
│       └── quick_add_memory.dart # Quick memory input
├── assets/                       # Images, icons, etc.
├── pubspec.yaml                  # Dependencies
└── README.md                     # This file
```

## Configuration

### API Configuration

The app is configured to connect to your Django backend. If you need to change the API URL, edit:

```dart
// lib/services/api_service.dart
static const String baseUrl = 'http://185.231.59.157/api/v1';
```

### Database Configuration

The app uses SQLite for local storage with automatic sync. No configuration needed.

## Features in Detail

### Authentication
- JWT token-based authentication
- Automatic token refresh
- Secure storage of credentials
- Offline authentication state

### Memory Management
- Create memories with rich content
- Categorize by type and priority
- Schedule reminders and notifications
- Mark as completed/pending
- Search and filter memories

### Offline Support
- Full offline functionality
- Automatic sync when online
- Conflict resolution
- Background sync

### AI Features
- Memory suggestions based on context
- Content enhancement
- Smart categorization
- Personalized recommendations

### Social Features
- Like and comment on memories
- Share memories with friends
- Organization-based sharing
- Privacy controls

## Troubleshooting

### Common Issues

1. **Build fails**: Run `flutter clean && flutter pub get`
2. **Dependencies issues**: Update Flutter SDK to latest version
3. **Android build issues**: Check Android SDK and build tools
4. **iOS build issues**: Update Xcode and iOS SDK

### Debug Mode

```bash
# Enable debug logging
flutter run --verbose

# Check device logs
flutter logs
```

### Performance Profiling

```bash
# Profile performance
flutter run --profile

# Analyze bundle size
flutter build apk --analyze-size
```

## Development

### Adding New Features

1. Create models in `lib/models/`
2. Add API endpoints in `lib/services/api_service.dart`
3. Create providers in `lib/providers/`
4. Build UI screens in `lib/screens/`
5. Add navigation in `lib/core/router.dart`

### Code Generation

If you add new models or services that use code generation:

```bash
flutter packages pub run build_runner build --delete-conflicting-outputs
```

### Testing

```bash
# Run unit tests
flutter test

# Run integration tests
flutter test integration_test/
```

## Deployment

### Android Play Store

1. Build app bundle: `flutter build appbundle --release`
2. Upload to Google Play Console
3. Configure store listing
4. Submit for review

### iOS App Store

1. Build iOS app: `flutter build ios --release`
2. Open in Xcode
3. Archive and upload to App Store Connect
4. Submit for review

## Support

For issues and questions:
1. Check Flutter documentation: https://docs.flutter.dev/
2. Review Memora backend documentation
3. Check GitHub issues and discussions

## License

This project is part of the Memora memory management system.
