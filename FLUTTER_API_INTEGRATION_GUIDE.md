# 📱 Flutter API Integration Guide

## 🎯 **Overview**

This guide shows how to integrate your Flutter app with the Memora smart reminder system. The API is optimized for mobile use with automatic smart reminder creation and efficient data retrieval.

## 🔑 **Authentication**

All endpoints require JWT authentication. Include the token in the Authorization header:

```dart
headers: {
  'Authorization': 'Bearer $accessToken',
  'Content-Type': 'application/json',
}
```

## 📋 **API Endpoints**

### **1. Create Memory with Auto-Reminders**

**Endpoint:** `POST /api/v1/flutter/memories/create/`

**Purpose:** Create a memory and automatically generate smart reminders based on content analysis.

**Request Body:**
```json
{
  "content": "Team meeting tomorrow at 2 PM to discuss quarterly goals",
  "memory_type": "task",                    // optional: general, task, idea, learning
  "importance": 8,                          // optional: 1-10 scale
  "delivery_date": "2024-01-15T14:00:00Z", // optional: ISO format
  "delivery_type": "scheduled",             // optional: scheduled, recurring, immediate
  "tags": ["work", "meeting"],              // optional: array of strings
  "privacy_level": "private",               // optional: private, friends, public
  "allow_comments": true,                   // optional: boolean
  "allow_likes": true                       // optional: boolean
}
```

**Response:**
```json
{
  "id": 123,
  "content": "Team meeting tomorrow at 2 PM...",
  "memory_type": "task",
  "importance": 8,
  "created_at": "2024-01-14T10:00:00Z",
  "created_reminders": [
    {
      "id": 456,
      "type": "time_based",
      "priority": "high",
      "next_trigger": "2024-01-15T13:45:00Z",
      "description": "Meeting reminder 15 minutes before scheduled time"
    }
  ],
  "reminder_count": 1
}
```

**Flutter Implementation:**
```dart
Future<Map<String, dynamic>> createMemory(Map<String, dynamic> memoryData) async {
  final response = await http.post(
    Uri.parse('$baseUrl/api/v1/flutter/memories/create/'),
    headers: {
      'Authorization': 'Bearer $accessToken',
      'Content-Type': 'application/json',
    },
    body: jsonEncode(memoryData),
  );
  
  if (response.statusCode == 201) {
    return jsonDecode(response.body);
  } else {
    throw Exception('Failed to create memory');
  }
}
```

### **2. Get Smart Reminders**

**Endpoint:** `GET /api/v1/flutter/reminders/`

**Purpose:** Retrieve all smart reminders for the user with filtering and pagination.

**Query Parameters:**
- `status`: `active`, `triggered`, `all` (default: `active`)
- `type`: `time_based`, `date_based`, `frequency_based`
- `priority`: `low`, `medium`, `high`, `critical`
- `limit`: number of results (default: 50)
- `offset`: pagination offset (default: 0)

**Response:**
```json
{
  "reminders": [
    {
      "id": 456,
      "reminder_type": "time_based",
      "priority": "high",
      "is_active": true,
      "next_trigger": "2024-01-15T13:45:00Z",
      "last_triggered": null,
      "memory": {
        "id": 123,
        "content": "Team meeting tomorrow at 2 PM...",
        "memory_type": "task"
      },
      "trigger_conditions": {
        "target_time": "2024-01-15T14:00:00Z",
        "advance_minutes": 15,
        "reason": "Meeting reminder 15 minutes before scheduled time"
      }
    }
  ],
  "total_count": 5,
  "has_more": false,
  "next_offset": null
}
```

**Flutter Implementation:**
```dart
Future<List<Map<String, dynamic>>> getReminders({
  String status = 'active',
  String? type,
  String? priority,
  int limit = 50,
  int offset = 0,
}) async {
  final queryParams = {
    'status': status,
    'limit': limit.toString(),
    'offset': offset.toString(),
  };
  
  if (type != null) queryParams['type'] = type;
  if (priority != null) queryParams['priority'] = priority;
  
  final uri = Uri.parse('$baseUrl/api/v1/flutter/reminders/')
      .replace(queryParameters: queryParams);
  
  final response = await http.get(
    uri,
    headers: {'Authorization': 'Bearer $accessToken'},
  );
  
  if (response.statusCode == 200) {
    final data = jsonDecode(response.body);
    return List<Map<String, dynamic>>.from(data['reminders']);
  } else {
    throw Exception('Failed to get reminders');
  }
}
```

### **3. Get Reminder Statistics**

**Endpoint:** `GET /api/v1/flutter/reminders/stats/`

**Purpose:** Get comprehensive statistics for dashboard display.

**Response:**
```json
{
  "total_reminders": 15,
  "active_reminders": 12,
  "upcoming_count": 3,
  "triggered_today": 2,
  "by_type": {
    "time_based": 8,
    "date_based": 4,
    "frequency_based": 3
  },
  "by_priority": {
    "high": 5,
    "medium": 7,
    "low": 3
  },
  "generated_at": "2024-01-14T10:00:00Z"
}
```

### **4. Check for Triggered Reminders**

**Endpoint:** `POST /api/v1/flutter/reminders/check/`

**Purpose:** Check for reminders that have been triggered (for background sync).

**Request Body (optional):**
```json
{
  "last_check": "2024-01-14T09:00:00Z"  // Only get reminders after this time
}
```

**Response:**
```json
{
  "triggered_count": 2,
  "reminders": [
    {
      "id": 456,
      "memory_id": 123,
      "memory_content": "Team meeting tomorrow at 2 PM...",
      "memory_type": "task",
      "reminder_type": "time_based",
      "priority": "high",
      "trigger_reason": "Meeting reminder 15 minutes before scheduled time",
      "triggered_at": "2024-01-15T13:45:00Z",
      "next_trigger": "2024-01-15T14:00:00Z"
    }
  ],
  "check_time": "2024-01-15T13:45:30Z"
}
```

### **5. Reminder Actions**

**Endpoint:** `POST /api/v1/flutter/reminders/{reminder_id}/actions/`

**Purpose:** Perform actions on reminders (snooze, dismiss, mark done).

**Request Body:**
```json
{
  "action": "snooze",    // snooze, dismiss, mark_done
  "hours": 2,           // for snooze action (optional, default: 1)
  "reason": "Busy now"  // optional reason
}
```

**Response:**
```json
{
  "success": true,
  "message": "Reminder snoozed for 2 hour(s)",
  "next_trigger": "2024-01-15T15:45:00Z"
}
```

**Flutter Implementation:**
```dart
Future<bool> performReminderAction(int reminderId, String action, {int? hours, String? reason}) async {
  final body = {'action': action};
  if (hours != null) body['hours'] = hours;
  if (reason != null) body['reason'] = reason;
  
  final response = await http.post(
    Uri.parse('$baseUrl/api/v1/flutter/reminders/$reminderId/actions/'),
    headers: {
      'Authorization': 'Bearer $accessToken',
      'Content-Type': 'application/json',
    },
    body: jsonEncode(body),
  );
  
  return response.statusCode == 200;
}
```

### **6. Get Memories with Reminders**

**Endpoint:** `GET /api/v1/flutter/memories/with-reminders/`

**Purpose:** Get memories along with their associated smart reminders.

**Query Parameters:**
- `memory_id`: specific memory ID (optional)
- `with_reminders`: include reminders in response (default: true)
- `limit`: number of results (default: 20)
- `offset`: pagination offset (default: 0)

## 🚀 **Flutter App Integration Flow**

### **1. Memory Creation Flow**

```dart
class MemoryService {
  Future<void> createMemoryWithReminders(String content, {
    String memoryType = 'general',
    int importance = 5,
    DateTime? deliveryDate,
    String deliveryType = 'immediate',
    List<String> tags = const [],
  }) async {
    try {
      final memoryData = {
        'content': content,
        'memory_type': memoryType,
        'importance': importance,
        'delivery_date': deliveryDate?.toIso8601String(),
        'delivery_type': deliveryType,
        'tags': tags,
      };
      
      final result = await createMemory(memoryData);
      
      // Show success message with reminder count
      final reminderCount = result['reminder_count'] ?? 0;
      if (reminderCount > 0) {
        showSnackBar('Memory created with $reminderCount smart reminder(s)!');
      } else {
        showSnackBar('Memory created successfully!');
      }
      
      // Refresh reminders list
      await refreshReminders();
      
    } catch (e) {
      showSnackBar('Failed to create memory: $e');
    }
  }
}
```

### **2. Reminder Management Flow**

```dart
class ReminderService {
  List<Map<String, dynamic>> _reminders = [];
  
  Future<void> loadReminders() async {
    try {
      _reminders = await getReminders(status: 'active');
      notifyListeners();
    } catch (e) {
      showSnackBar('Failed to load reminders: $e');
    }
  }
  
  Future<void> checkTriggeredReminders() async {
    try {
      final result = await checkReminders();
      final triggeredCount = result['triggered_count'] ?? 0;
      
      if (triggeredCount > 0) {
        // Show notification or update UI
        _showTriggeredReminders(result['reminders']);
      }
    } catch (e) {
      print('Failed to check reminders: $e');
    }
  }
  
  Future<void> snoozeReminder(int reminderId, int hours) async {
    try {
      await performReminderAction(reminderId, 'snooze', hours: hours);
      await loadReminders(); // Refresh list
      showSnackBar('Reminder snoozed for $hours hour(s)');
    } catch (e) {
      showSnackBar('Failed to snooze reminder: $e');
    }
  }
  
  Future<void> dismissReminder(int reminderId) async {
    try {
      await performReminderAction(reminderId, 'dismiss');
      await loadReminders(); // Refresh list
      showSnackBar('Reminder dismissed');
    } catch (e) {
      showSnackBar('Failed to dismiss reminder: $e');
    }
  }
}
```

### **3. Background Sync**

```dart
class BackgroundSyncService {
  Timer? _syncTimer;
  
  void startBackgroundSync() {
    _syncTimer = Timer.periodic(Duration(minutes: 5), (timer) {
      _checkForTriggeredReminders();
    });
  }
  
  void stopBackgroundSync() {
    _syncTimer?.cancel();
  }
  
  Future<void> _checkForTriggeredReminders() async {
    try {
      final result = await checkReminders();
      final triggeredCount = result['triggered_count'] ?? 0;
      
      if (triggeredCount > 0) {
        // Show local notification
        await _showLocalNotification(triggeredCount);
        
        // Update app state
        await reminderService.loadReminders();
      }
    } catch (e) {
      print('Background sync failed: $e');
    }
  }
  
  Future<void> _showLocalNotification(int count) async {
    // Implement local notification
    // Use flutter_local_notifications package
  }
}
```

## 📊 **Dashboard Integration**

```dart
class DashboardService {
  Future<Map<String, dynamic>> getDashboardData() async {
    try {
      final stats = await getReminderStats();
      final upcomingReminders = await getReminders(
        status: 'active',
        limit: 5,
      );
      
      return {
        'stats': stats,
        'upcoming_reminders': upcomingReminders,
      };
    } catch (e) {
      throw Exception('Failed to load dashboard data: $e');
    }
  }
}
```

## 🔧 **Error Handling**

```dart
class ApiErrorHandler {
  static void handleError(dynamic error, String context) {
    if (error is SocketException) {
      showSnackBar('No internet connection');
    } else if (error is TimeoutException) {
      showSnackBar('Request timeout. Please try again.');
    } else if (error is HttpException) {
      showSnackBar('Server error. Please try again later.');
    } else {
      showSnackBar('$context failed: $error');
    }
  }
}
```

## 🎯 **Key Benefits**

✅ **Automatic Smart Reminders**: No need to manually create reminders - they're generated automatically based on memory content

✅ **Optimized for Mobile**: Lightweight responses and efficient data structures

✅ **Real-time Sync**: Background checking for triggered reminders

✅ **Comprehensive Actions**: Snooze, dismiss, and mark done functionality

✅ **Rich Statistics**: Dashboard-ready statistics and analytics

✅ **Flexible Filtering**: Filter reminders by type, priority, and status

✅ **Pagination Support**: Efficient handling of large reminder lists

## 🚀 **Getting Started**

1. **Set up authentication** with JWT tokens
2. **Create memories** using the optimized endpoint
3. **Implement reminder management** with the provided actions
4. **Add background sync** for real-time updates
5. **Build dashboard** with statistics and upcoming reminders

The API is designed to work seamlessly with your Flutter app, providing all the smart reminder functionality with minimal complexity!




