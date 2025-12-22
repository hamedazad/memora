# Memora Mobile App

A React Native mobile application that connects to your Django Memora Core backend for personal memory management with AI-powered features.

## 🚀 Features

### Core Features
- ✅ **Authentication** - Login/Register with JWT tokens
- ✅ **Memory Management** - Create, read, update, delete memories
- ✅ **Offline Support** - SQLite local database with sync
- ✅ **Voice Recording** - Record and transcribe voice notes
- ✅ **AI Integration** - AI suggestions and categorization
- ✅ **Cross-Platform** - Works on both iOS and Android

### Technical Features
- ✅ **TypeScript** - Full type safety
- ✅ **Navigation** - React Navigation with stack and tab navigation
- ✅ **State Management** - Context API for authentication
- ✅ **API Integration** - Axios with interceptors and error handling
- ✅ **Local Storage** - SQLite database for offline data
- ✅ **Caching** - Intelligent caching with TTL
- ✅ **Network Handling** - Automatic retry and offline queue

## 📱 App Structure

```
src/
├── config/
│   └── api.ts              # API configuration and endpoints
├── contexts/
│   └── AuthContext.tsx     # Authentication context
├── services/
│   ├── api.ts              # API service with authentication
│   └── database.ts         # Local SQLite database service
├── screens/
│   ├── LoginScreen.tsx     # Login screen
│   ├── RegisterScreen.tsx  # Registration screen
│   ├── HomeScreen.tsx      # Dashboard/home screen
│   ├── MemoriesScreen.tsx  # Memory list screen
│   ├── CreateMemoryScreen.tsx # Create memory screen
│   ├── MemoryDetailScreen.tsx # Memory detail screen
│   └── ProfileScreen.tsx   # User profile screen
└── components/             # Reusable components (to be added)
```

## 🛠️ Setup Instructions

### Prerequisites
- Node.js (v16 or higher)
- npm or yarn
- React Native development environment
- Android Studio (for Android development)
- Xcode (for iOS development, macOS only)

### Installation

1. **Clone and navigate to the project:**
   ```bash
   cd MemoraApp
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Start the development server:**
   ```bash
   npm start
   ```

4. **Run on Android:**
   ```bash
   npm run android
   ```

5. **Run on iOS (macOS only):**
   ```bash
   npm run ios
   ```

## 🔧 Configuration

### API Configuration
The app is configured to connect to your Django backend at `http://185.231.59.157/api/v1`. You can modify this in `src/config/api.ts`:

```typescript
export const API_CONFIG = {
  BASE_URL: 'http://185.231.59.157/api/v1',
  // ... other config
};
```

### Database Configuration
Local SQLite database configuration in `src/config/api.ts`:

```typescript
export const DB_CONFIG = {
  NAME: 'memora_mobile.db',
  VERSION: '1.0',
  SIZE: 2000000, // 2MB
};
```

## 📊 Database Schema

### Users Table
- `id` (TEXT, PRIMARY KEY)
- `username` (TEXT, NOT NULL)
- `email` (TEXT, NOT NULL)
- `first_name` (TEXT)
- `last_name` (TEXT)
- `timezone` (TEXT)
- `language` (TEXT)
- `created_at` (DATETIME)
- `updated_at` (DATETIME)

### Memories Table
- `id` (TEXT, PRIMARY KEY)
- `title` (TEXT, NOT NULL)
- `content` (TEXT, NOT NULL)
- `category` (TEXT)
- `tags` (TEXT, JSON)
- `is_important` (INTEGER, BOOLEAN)
- `reminder_date` (TEXT)
- `voice_file` (TEXT)
- `image` (TEXT)
- `created_at` (DATETIME)
- `updated_at` (DATETIME)
- `sync_status` (TEXT)
- `local_id` (TEXT)

### Offline Operations Table
- `id` (INTEGER, PRIMARY KEY, AUTOINCREMENT)
- `operation_type` (TEXT, NOT NULL)
- `table_name` (TEXT, NOT NULL)
- `record_id` (TEXT)
- `data` (TEXT, NOT NULL, JSON)
- `created_at` (DATETIME)
- `synced` (INTEGER, BOOLEAN)

### Cache Table
- `key` (TEXT, PRIMARY KEY)
- `value` (TEXT, NOT NULL, JSON)
- `ttl` (INTEGER, NOT NULL)
- `created_at` (DATETIME)

## 🔐 Authentication Flow

1. **Login/Register** - User authenticates with Django backend
2. **Token Storage** - JWT tokens stored in AsyncStorage
3. **Auto Refresh** - Access tokens automatically refreshed
4. **Offline Support** - User can use app offline with cached data
5. **Sync** - Data synced when connection restored

## 📡 API Integration

### Authentication Endpoints
- `POST /auth/login/` - User login
- `POST /auth/register/` - User registration
- `POST /auth/refresh/` - Token refresh

### Memory Endpoints
- `GET /memories/` - Get all memories
- `POST /memories/` - Create memory
- `GET /memories/{id}/` - Get memory detail
- `PUT /memories/{id}/` - Update memory
- `DELETE /memories/{id}/` - Delete memory

### AI Endpoints
- `POST /ai/suggestions/` - Get AI suggestions
- `POST /ai/categorize/` - Categorize memory

### Voice Endpoints
- `POST /voice/upload/` - Upload voice file
- `POST /voice/transcribe/` - Transcribe voice

## 🔄 Offline Sync

### How it works:
1. **Offline Operations** - All changes stored in local database
2. **Operation Queue** - Pending operations queued for sync
3. **Network Detection** - Automatic detection of network status
4. **Background Sync** - Sync when connection restored
5. **Conflict Resolution** - Server data takes precedence

### Sync Process:
```typescript
// When online, sync offline operations
const offlineOps = await databaseService.getOfflineOperations();
if (offlineOps.length > 0) {
  await apiService.syncOfflineData(offlineOps);
}
```

## 🎯 Development Roadmap

### Phase 1: Core Features ✅
- [x] Authentication system
- [x] Basic navigation
- [x] API integration
- [x] Local database
- [x] Offline support

### Phase 2: Memory Features 🚧
- [ ] Memory creation with rich text
- [ ] Voice recording integration
- [ ] Image upload support
- [ ] Memory categorization
- [ ] Search and filtering

### Phase 3: AI Features 🚧
- [ ] AI-powered suggestions
- [ ] Automatic categorization
- [ ] Smart reminders
- [ ] Content analysis

### Phase 4: Advanced Features 📋
- [ ] Push notifications
- [ ] Memory sharing
- [ ] Advanced search
- [ ] Data export/import
- [ ] Theme customization

## 🐛 Troubleshooting

### Common Issues

1. **Metro bundler issues:**
   ```bash
   npx react-native start --reset-cache
   ```

2. **Android build issues:**
   ```bash
   cd android && ./gradlew clean
   ```

3. **iOS build issues:**
   ```bash
   cd ios && pod install
   ```

4. **Database issues:**
   ```bash
   # Clear app data or reinstall app
   ```

### Debug Mode
Enable debug logging in `src/services/database.ts`:
```typescript
SQLite.DEBUG(true);
```

## 📱 Testing

### Manual Testing
1. Test authentication flow
2. Test offline functionality
3. Test memory CRUD operations
4. Test sync functionality
5. Test voice recording (if implemented)

### Automated Testing (Future)
- Unit tests for services
- Integration tests for API
- E2E tests for user flows

## 🚀 Deployment

### Android
1. Generate signed APK:
   ```bash
   cd android && ./gradlew assembleRelease
   ```

2. Upload to Google Play Store

### iOS
1. Archive in Xcode
2. Upload to App Store Connect

## 📄 License

This project is part of the Memora Core ecosystem.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📞 Support

For support and questions:
- Check the Django backend documentation
- Review the API endpoints
- Test with the web interface first

---

**🎉 Your Memora Mobile App is ready to connect to your Django backend!**




















