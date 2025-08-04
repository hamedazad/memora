# Memora Mobile App

A React Native mobile application for the Memora Memory Assistant platform, featuring AI-powered memory management, offline sync, voice input, and push notifications.

## 🚀 Features

### Core Features
- **Memory Management**: Create, edit, delete, and organize memories
- **AI-Powered**: Automatic summarization, tagging, and importance scoring
- **Voice Input**: Speech-to-text for hands-free memory creation
- **Search**: Advanced search with voice search capabilities
- **Offline Sync**: Work offline with automatic sync when online
- **Push Notifications**: Memory reminders and AI suggestions

### Advanced Features
- **Biometric Authentication**: Fingerprint/face ID support
- **Camera Integration**: Add photos to memories
- **Location Tagging**: Automatically tag memories with location
- **Mood Tracking**: Track emotional context of memories
- **Analytics**: Memory patterns and insights
- **Export/Import**: Backup and restore memories

### Technical Features
- **Cross-Platform**: iOS and Android support
- **TypeScript**: Full type safety
- **Modern UI**: Material Design with React Native Paper
- **State Management**: Context API with Zustand
- **Data Fetching**: React Query for efficient caching
- **Navigation**: React Navigation with bottom tabs

## 📱 Screenshots

*Screenshots will be added here*

## 🛠 Tech Stack

### Core
- **React Native**: 0.72.6
- **TypeScript**: 4.8.4
- **React**: 18.2.0

### Navigation & UI
- **React Navigation**: 6.1.9
- **React Native Paper**: 5.11.1
- **React Native Elements**: 3.4.3
- **React Native Vector Icons**: 10.0.2

### State Management & Data
- **React Query**: 3.39.3
- **Zustand**: 4.4.1
- **AsyncStorage**: 1.19.5
- **SQLite**: 6.0.1

### Voice & Media
- **React Native Voice**: 0.3.0
- **React Native TTS**: 4.1.0
- **React Native Camera**: 4.2.1
- **React Native Image Picker**: 5.6.0

### Notifications & Sync
- **React Native Push Notification**: 8.1.1
- **Firebase**: 18.7.3
- **NetInfo**: 9.4.1

### Security & Authentication
- **React Native Keychain**: 8.1.3
- **React Native Biometrics**: 3.0.1
- **React Native Permissions**: 3.10.1

## 📋 Prerequisites

### Development Environment
- **Node.js**: 16.0 or later
- **npm**: 8.0 or later
- **React Native CLI**: Latest version
- **Android Studio**: For Android development
- **Xcode**: For iOS development (macOS only)

### System Requirements
- **Android**: API level 21+ (Android 5.0+)
- **iOS**: iOS 12.0+
- **RAM**: 8GB minimum, 16GB recommended
- **Storage**: 10GB free space

## 🚀 Installation

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/memora-mobile.git
cd memora-mobile
```

### 2. Install Dependencies
```bash
npm install
# or
yarn install
```

### 3. iOS Setup (macOS only)
```bash
cd ios
pod install
cd ..
```

### 4. Environment Configuration
Create a `.env` file in the root directory:
```env
# API Configuration
API_BASE_URL=http://localhost:8000/api/v1
API_TIMEOUT=30000

# Firebase Configuration (for notifications)
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_API_KEY=your-api-key

# Feature Flags
ENABLE_VOICE_SEARCH=true
ENABLE_BIOMETRIC_AUTH=true
ENABLE_CAMERA=true
```

### 5. Android Setup
1. Open Android Studio
2. Open the `android` folder
3. Sync Gradle files
4. Build the project

## 🏃‍♂️ Running the App

### Development Mode
```bash
# Start Metro bundler
npm start
# or
yarn start

# Run on Android
npm run android
# or
yarn android

# Run on iOS (macOS only)
npm run ios
# or
yarn ios
```

### Production Build
```bash
# Android
npm run build:android
# or
yarn build:android

# iOS (macOS only)
npm run build:ios
# or
yarn build:ios
```

## 📁 Project Structure

```
src/
├── components/          # Reusable UI components
│   ├── TabBarIcon.tsx
│   └── LoadingScreen.tsx
├── navigation/          # Navigation configuration
│   └── AppNavigator.tsx
├── screens/            # Screen components
│   ├── auth/          # Authentication screens
│   ├── main/          # Main app screens
│   └── memories/      # Memory-related screens
├── services/           # API and external services
│   ├── apiService.ts
│   ├── authService.ts
│   ├── memoryService.ts
│   ├── syncService.ts
│   └── notificationService.ts
├── store/             # State management
│   ├── AuthContext.tsx
│   ├── MemoryContext.tsx
│   └── NotificationContext.tsx
├── types/             # TypeScript type definitions
│   └── index.ts
├── utils/             # Utility functions
│   └── theme.ts
└── assets/            # Static assets
    ├── images/
    └── icons/
```

## 🔧 Configuration

### API Configuration
The app connects to the Django backend API. Update the API configuration in `src/services/apiService.ts`:

```typescript
const baseURL = process.env.API_BASE_URL || 'http://localhost:8000/api/v1';
```

### Theme Configuration
Customize the app theme in `src/utils/theme.ts`:

```typescript
export const lightTheme = {
  colors: {
    primary: '#6200EE',
    secondary: '#03DAC6',
    // ... other colors
  }
};
```

### Navigation Configuration
Update navigation in `src/navigation/AppNavigator.tsx`:

```typescript
const MainTabNavigator = () => (
  <Tab.Navigator>
    <Tab.Screen name="Home" component={HomeScreen} />
    <Tab.Screen name="Memories" component={MemoryStack} />
    // ... other tabs
  </Tab.Navigator>
);
```

## 🧪 Testing

### Run Tests
```bash
npm test
# or
yarn test
```

### Test Coverage
```bash
npm run test:coverage
# or
yarn test:coverage
```

## 📦 Building for Production

### Android
1. Generate a signed APK:
```bash
cd android
./gradlew assembleRelease
```

2. The APK will be in `android/app/build/outputs/apk/release/`

### iOS
1. Open the project in Xcode
2. Select your team and bundle identifier
3. Archive and distribute

## 🔐 Security Features

- **Biometric Authentication**: Fingerprint/face ID support
- **Secure Storage**: Encrypted local storage
- **Token Management**: Automatic token refresh
- **Network Security**: HTTPS-only API calls
- **Permission Handling**: Granular permission requests

## 🔄 Offline Sync

The app supports offline functionality with automatic sync:

- **Local Storage**: SQLite database for offline data
- **Sync Queue**: Pending changes stored locally
- **Conflict Resolution**: Automatic conflict detection
- **Background Sync**: Sync when network is available

## 📱 Platform-Specific Features

### Android
- Material Design components
- Android-specific navigation patterns
- Background job processing
- Custom notification channels

### iOS
- iOS-specific UI patterns
- Face ID/Touch ID integration
- iOS notification handling
- Background app refresh

## 🐛 Troubleshooting

### Common Issues

1. **Metro bundler issues**:
```bash
npx react-native start --reset-cache
```

2. **iOS build issues**:
```bash
cd ios && pod install && cd ..
```

3. **Android build issues**:
```bash
cd android && ./gradlew clean && cd ..
```

4. **Permission issues**:
- Check device settings
- Reinstall the app
- Clear app data

### Debug Mode
Enable debug mode in development:
```bash
# Android
adb reverse tcp:8081 tcp:8081

# iOS
# Use Xcode debugger
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: Check the [Wiki](../../wiki)
- **Issues**: Report bugs on [GitHub Issues](../../issues)
- **Discussions**: Join the [GitHub Discussions](../../discussions)

## 🔄 Version History

- **v1.0.0**: Initial release with core features
- **v1.1.0**: Added voice search and biometric auth
- **v1.2.0**: Enhanced offline sync and notifications

## 📞 Contact

- **Email**: support@memora.app
- **Website**: https://memora.app
- **Twitter**: @memora_app

---

Made with ❤️ by the Memora Team 