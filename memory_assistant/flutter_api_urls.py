from django.urls import path
from . import flutter_api_views
from . import fcm_token_api

# Flutter-optimized API URL patterns
urlpatterns = [
    # Memory creation with automatic smart reminders
    path('flutter/memories/create/', flutter_api_views.FlutterMemoryAPIView.as_view(), name='flutter-memory-create'),
    path('flutter/memories/quick-add/', flutter_api_views.FlutterQuickAddMemoryAPIView.as_view(), name='flutter-memory-quick-add'),
    
    # Smart reminders management - specific endpoints first to avoid URL conflicts
    path('flutter/reminders/memory/<int:memory_id>/', flutter_api_views.FlutterRemindersForMemoryAPIView.as_view(), name='flutter-reminders-for-memory'),
    path('flutter/reminders/check/', flutter_api_views.FlutterReminderCheckAPIView.as_view(), name='flutter-reminder-check'),
    path('flutter/reminders/stats/', flutter_api_views.FlutterReminderStatsAPIView.as_view(), name='flutter-reminder-stats'),
    path('flutter/reminders/scheduled/', flutter_api_views.FlutterScheduledRemindersAPIView.as_view(), name='flutter-reminders-scheduled'),
    path('flutter/reminders/<int:reminder_id>/actions/', flutter_api_views.FlutterReminderActionsAPIView.as_view(), name='flutter-reminder-actions'),
    path('flutter/reminders/<int:reminder_id>/', flutter_api_views.FlutterSmartReminderAPIView.as_view(), name='flutter-reminder-detail'),
    path('flutter/reminders/', flutter_api_views.FlutterSmartReminderAPIView.as_view(), name='flutter-reminders'),
    
    # Direct API endpoints that Flutter app calls
    path('smart-reminders/scheduled/', flutter_api_views.FlutterScheduledRemindersAPIView.as_view(), name='api-reminders-scheduled'),
    
    # Memories with reminders
    path('flutter/memories/with-reminders/', flutter_api_views.FlutterMemoryWithRemindersAPIView.as_view(), name='flutter-memories-with-reminders'),
    
    # Scheduled memory actions
    path('flutter/memories/<int:memory_id>/scheduled-actions/', flutter_api_views.FlutterScheduledMemoryActionsAPIView.as_view(), name='flutter-scheduled-memory-actions'),
    
    # FCM Token Management
    path('flutter/fcm/register/', fcm_token_api.register_fcm_token, name='flutter-fcm-register'),
    path('flutter/fcm/settings/', fcm_token_api.get_notification_settings, name='flutter-fcm-settings'),
    path('flutter/fcm/settings/update/', fcm_token_api.update_notification_settings, name='flutter-fcm-settings-update'),
    path('flutter/fcm/test/', fcm_token_api.test_notification, name='flutter-fcm-test'),
]

