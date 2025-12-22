# API Endpoint Mapping & Synchronization Guide

**Version:** 1.0.0  
**Last Updated:** 2025-01-12  
**Status:** ✅ Synchronized

---

## 📋 Overview

This document maps all API endpoints between the **memora_mobile** Flutter app and the **memora_core** Django backend, ensuring both applications stay synchronized.

## 🔗 Base URLs

### Mobile App Configuration
```dart
// Development (local)
http://localhost:8000/api/v1           // iOS Simulator
http://10.0.2.2:8000/api/v1            // Android Emulator

// Production
https://api.memora.app/api/v1
```

### Backend Configuration
```python
# Django settings
ALLOWED_HOSTS = ['127.0.0.1', 'localhost', '0.0.0.0', 'api.memora.app']
SCHEMA_PATH_PREFIX = '/api/v1/'
```

---

## 📊 Complete Endpoint Mapping

### 🔐 Authentication Endpoints

| Mobile Constant | Mobile Path | Backend URL | Backend View | Status |
|----------------|-------------|-------------|--------------|--------|
| `healthEndpoint` | `/health/` | `/api/v1/health/` | `HealthCheckView.get` | ✅ Synced |
| `loginEndpoint` | `/auth/token/` | `/api/v1/auth/login/` <br> `/api/v1/auth/token/` | `CustomTokenObtainPairView` | ✅ Synced |
| `registerEndpoint` | `/auth/register/` | `/api/v1/auth/register/` | `RegisterView.post` | ✅ Synced |
| `refreshEndpoint` | `/auth/refresh/` | `/api/v1/auth/token/refresh/` | `TokenRefreshView` | ⚠️ Path Mismatch |
| `logoutEndpoint` | `/auth/logout/` | N/A (client-side) | - | ℹ️ Client Only |

**Action Required:**
- ⚠️ Update mobile `refreshEndpoint` from `/auth/refresh/` to `/auth/token/refresh/`

---

### 📝 Memory Endpoints

| Mobile Constant | Mobile Path | Backend URL | Backend View | Status |
|----------------|-------------|-------------|--------------|--------|
| `memoriesEndpoint` | `/memories/` | `/api/v1/memories/` | `MemoryViewSet` | ✅ Synced |
| `searchEndpoint` | `/memories/search/` | `/api/v1/memories/search/` | `MemoryViewSet.search` | ✅ Synced |
| `semanticSearchEndpoint` | `/memories/semantic-search/` | `/api/v1/search/semantic` | `SemanticSearchView` | ⚠️ Path Mismatch |
| `quickAddEndpoint` | `/memories/quick-add/` | `/api/v1/memories/quick-add/` | `MemoryViewSet.quick_add` | ✅ Synced |
| `dashboardStatsEndpoint` | `/memories/dashboard-stats/` | `/api/v1/memories/dashboard-stats/` | `MemoryViewSet.dashboard_stats` | ✅ Synced |
| `memoryLikeEndpoint` | `/memories/{id}/like/` | `/api/v1/memories/{pk}/like/` | `MemoryViewSet.like` | ✅ Synced |
| `memoryCommentEndpoint` | `/memories/{id}/comment/` | `/api/v1/memories/{pk}/comment/` | `MemoryViewSet.comment` | ✅ Synced |
| `memorySimilarEndpoint` | `/memories/{id}/similar/` | `/api/v1/memories/{pk}/similar/` | `MemoryViewSet.similar` | ✅ Synced |
| `memoryArchiveEndpoint` | `/memories/{id}/archive/` | `/api/v1/memories/{pk}/archive/` | Custom Action | ℹ️ To Implement |
| `memoryUnarchiveEndpoint` | `/memories/{id}/unarchive/` | `/api/v1/memories/{pk}/unarchive/` | Custom Action | ℹ️ To Implement |

**Action Required:**
- ⚠️ Standardize semantic search path to `/api/v1/search/semantic` in both apps
- ℹ️ Implement archive/unarchive actions in backend `MemoryViewSet`

---

### ⏰ Smart Reminders Endpoints

#### Flutter-Optimized Endpoints (Preferred)

| Mobile Constant | Mobile Path | Backend URL | Backend View | Status |
|----------------|-------------|-------------|--------------|--------|
| `flutterRemindersBase` | `/flutter/reminders/` | `/api/v1/flutter/reminders/` | `FlutterSmartReminderAPIView` | ✅ Synced |
| `flutterRemindersCheck` | `/flutter/reminders/check/` | `/api/v1/flutter/reminders/check/` | `FlutterReminderCheckAPIView` | ✅ Synced |
| `flutterRemindersStats` | `/flutter/reminders/stats/` | `/api/v1/flutter/reminders/stats/` | `FlutterReminderStatsAPIView` | ✅ Synced |
| `flutterRemindersForMemory` | `/flutter/reminders/memory/` | `/api/v1/flutter/reminders/memory/{memory_id}/` | `FlutterRemindersForMemoryAPIView` | ✅ Synced |
| `flutterMemoryWithReminders` | `/flutter/memories/with-reminders/` | `/api/v1/flutter/memories/with-reminders/` | `FlutterMemoryWithRemindersAPIView` | ✅ Synced |
| `flutterMemoryCreate` | `/flutter/memories/create/` | `/api/v1/flutter/memories/create/` | `FlutterMemoryAPIView.post` | ✅ Synced |
| `flutterScheduledMemoryActions` | `/flutter/memories/` | `/api/v1/flutter/memories/{memory_id}/scheduled-actions/` | `FlutterScheduledMemoryActionsAPIView` | ✅ Synced |

#### Legacy Endpoints (Deprecated)

| Mobile Constant | Mobile Path | Backend URL | Status |
|----------------|-------------|-------------|--------|
| `smartRemindersBase` | `/smart-reminders/` | `/api/v1/smart-reminders/` | 🔶 Deprecated |
| `smartRemindersAnalyze` | `/smart-reminders/analyze/` | `/api/v1/smart-reminders/analyze/` | 🔶 Deprecated |
| `smartRemindersScheduled` | `/smart-reminders/scheduled/` | `/api/v1/smart-reminders/scheduled/` <br> `/api/v1/flutter/reminders/scheduled/` | 🔶 Use Flutter endpoint |
| `smartRemindersCheckTriggers` | `/smart-reminders/check/` | `/api/v1/smart-reminders/check/` | 🔶 Deprecated |
| `smartRemindersStats` | `/smart-reminders/stats/` | `/api/v1/smart-reminders/stats/` | 🔶 Deprecated |

**Action Required:**
- 🔶 Deprecate legacy endpoints in mobile app v2.0.0
- ✅ Use `/flutter/reminders/*` endpoints exclusively

---

### 🤖 AI Features Endpoints

| Mobile Constant | Mobile Path | Backend URL | Backend View | Status |
|----------------|-------------|-------------|--------------|--------|
| `aiSuggestionsEndpoint` | `/ai/suggestions/` | `/api/v1/ai/suggestions/` | `AIViewSet.suggestions` | ✅ Synced |
| `aiEnhanceEndpoint` | `/ai/enhance/` | `/api/v1/ai/enhance/` <br> `/api/v1/ai/enhance-memory/` | `AIViewSet.enhance_memory` | ✅ Synced |
| `aiCategorizeEndpoint` | `/ai/categorize/` | `/api/v1/ai/categorize` | `AIViewSet.categorize` | ✅ Synced |
| `aiSummaryEndpoint` | `/ai/summary/` | `/api/v1/ai/summarize` | `AIViewSet.summarize` | ⚠️ Path Mismatch |
| `aiTagsEndpoint` | `/ai/tags/` | `/api/v1/ai/tags` | `AIViewSet.tags` | ✅ Synced |
| `aiStatusEndpoint` | `/ai/status/` | `/api/v1/ai/status/` | `AIStatusView.get` | ✅ Synced |

**Action Required:**
- ⚠️ Standardize AI summary endpoint: mobile uses `/ai/summary/`, backend uses `/ai/summarize`

---

### 🎤 Voice Features Endpoints

| Mobile Constant | Mobile Path | Backend URL | Backend View | Status |
|----------------|-------------|-------------|--------------|--------|
| `voiceTranscribeEndpoint` | `/voice/transcribe/` | `/api/v1/voice/transcribe/` | `VoiceTranscribeView.post` | ⚠️ Mock Implementation |
| `voiceSearchEndpoint` | `/voice/search/` | `/api/v1/search/voice/` | `VoiceSearchView.post` | ✅ Synced |

**Action Required:**
- ⚠️ Implement actual voice transcription service (currently returns mock data)
- ⚠️ Add voice enhancement endpoint

---

### 👥 Social Features Endpoints

| Mobile Constant | Mobile Path | Backend URL | Backend View | Status |
|----------------|-------------|-------------|--------------|--------|
| `friendsEndpoint` | `/friends/` | `/api/v1/friends/` | `FriendsViewSet` | ℹ️ To Verify |
| `friendRequestsEndpoint` | `/friend-requests/` | `/api/v1/friend-requests/` | `FriendRequestsViewSet` | ℹ️ To Verify |
| `userSearchEndpoint` | `/users/search/` | `/api/v1/users/search/` | `UserViewSet.search` | ℹ️ To Verify |
| `shareMemoryEndpoint` | `/memories/{id}/share/` | `/api/v1/memories/{pk}/share/` | `MemoryViewSet.share` | ℹ️ To Verify |
| `sharedMemoriesEndpoint` | `/shared-with-me/` | `/api/v1/shared-with-me/` | `SharedMemoriesViewSet` | ℹ️ To Verify |
| `notificationsEndpoint` | `/notifications/` | `/api/v1/notifications/` | `NotificationsViewSet` | ℹ️ To Verify |

**Action Required:**
- ℹ️ Verify and test all social feature endpoints

---

## 🔄 Endpoint Synchronization Status

### ✅ Fully Synced (21 endpoints)
- Health check
- Authentication (login, register)
- Memory CRUD operations
- Smart reminders (Flutter endpoints)
- Most AI features
- Memory actions (like, comment, similar)

### ⚠️ Needs Attention (5 endpoints)
1. Token refresh path mismatch
2. Semantic search path inconsistency
3. AI summary endpoint naming
4. Voice transcription (mock implementation)
5. Archive/unarchive memory actions

### ℹ️ Needs Verification (6 endpoints)
- All social feature endpoints

### 🔶 Deprecated (5 endpoints)
- Legacy smart reminder endpoints

---

## 📖 How to Use This Document

### For Backend Developers
1. When adding a new endpoint, update this document first
2. Ensure endpoint follows naming conventions
3. Add OpenAPI schema annotations to views
4. Run endpoint validation tests
5. Notify mobile team of changes

### For Mobile Developers
1. Check this document before implementing new API calls
2. Use Flutter-optimized endpoints (`/flutter/*`) when available
3. Update `app_constants.dart` to match backend paths
4. Run endpoint validation tests after changes
5. Handle deprecated endpoints gracefully

---

## 🧪 Validation

### Run Backend Tests
```bash
cd c:\memora_core
python manage.py test memory_assistant.tests.test_api_endpoints
```

### Run Mobile Tests
```bash
cd c:\memora_mobile\memora_phone
flutter test test/integration/api_endpoint_test.dart
```

### View API Documentation
- **Swagger UI:** http://localhost:8000/api/docs/
- **ReDoc:** http://localhost:8000/api/redoc/
- **OpenAPI Schema:** http://localhost:8000/api/schema/

---

## 📅 Version History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0.0 | 2025-01-12 | Initial endpoint mapping documentation | System |

---

## 🔗 Related Documents

- [API Versioning Strategy](./API_VERSIONING_STRATEGY.md)
- [Backend API Documentation](http://localhost:8000/api/docs/)
- [Mobile App Constants](../memora_mobile/memora_phone/lib/constants/app_constants.dart)
- [Integration Tests](./tests/integration/test_api_sync.py)

---

**Note:** This document is auto-generated from code annotations and manual verification. Keep it updated with every API change.































