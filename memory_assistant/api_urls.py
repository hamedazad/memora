from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
from . import api_views
from . import flutter_api_urls
from . import unified_search_views

# Create router for ViewSets
router = DefaultRouter()
router.register(r'memories', api_views.MemoryViewSet, basename='memory')
router.register(r'users', api_views.UserViewSet, basename='user')
router.register(r'ai', api_views.AIViewSet, basename='ai')
router.register(r'smart-reminders', api_views.SmartReminderViewSet, basename='smart-reminder')

# API URL patterns
urlpatterns = [
    # Health check endpoint
    path('health/', api_views.HealthCheckView.as_view(), name='health_check'),
    
    # AI status endpoint
    path('ai/status/', api_views.AIStatusView.as_view(), name='ai-status'),
    
    # Authentication endpoints
    path('auth/register/', api_views.RegisterView.as_view(), name='register'),
    path('auth/login/', api_views.CustomTokenObtainPairView.as_view(), name='auth_login'),
    path('auth/token/', api_views.CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    
    # Place explicit endpoints BEFORE router include to avoid shadowing
    path('memories/quick-add/', api_views.MemoryViewSet.as_view({'post': 'quick_add'}), name='memory-quick-add'),
    path('memories/search/', unified_search_views.UnifiedSearchView.as_view(), name='memory-search-unified'),
    path('memories/dashboard-stats/', api_views.MemoryViewSet.as_view({'get': 'dashboard_stats'}), name='memory-dashboard-stats'),
    path('memories/<int:pk>/like/', api_views.MemoryViewSet.as_view({'post': 'like'}), name='memory-like'),
    path('memories/<int:pk>/comment/', api_views.MemoryViewSet.as_view({'post': 'comment'}), name='memory-comment'),
    path('memories/<int:pk>/similar/', api_views.MemoryViewSet.as_view({'get': 'similar'}), name='memory-similar'),
    
    # Router URLs (must come after explicit overrides)
    path('', include(router.urls)),
    
    # User endpoints
    path('users/profile/', api_views.UserViewSet.as_view({'get': 'profile'}), name='user-profile'),
    path('users/update-profile/', api_views.UserViewSet.as_view({'put': 'update_profile'}), name='user-update-profile'),
    
    # Voice processing endpoints
    path('voice/transcribe/', api_views.VoiceTranscribeView.as_view(), name='voice-transcribe'),
    path('voice/enhance/', api_views.VoiceTranscribeView.as_view(), name='voice-enhance'),  # Using same view for now
    path('memories/<int:pk>/voice/', api_views.MemoryViewSet.as_view({'post': 'upload_voice'}), name='memory-voice-upload'),
    
    # Search utilities
    path('search/suggestions/', unified_search_views.SearchSuggestionsView.as_view(), name='search-suggestions'),
    
    # Legacy search endpoints (deprecated - use /memories/search/ with mode parameter instead)
    path('search/memories', api_views.SearchMemoriesView.as_view(), name='search-memories-legacy'),
    path('search/semantic', api_views.SemanticSearchView.as_view(), name='semantic-search-legacy'),
    path('search/voice/', api_views.VoiceSearchView.as_view(), name='voice-search'),
    
    # Stats endpoint
    path('memories/stats', api_views.MemoryStatsView.as_view(), name='memory-stats'),
    
    # AI endpoints
    path('ai/suggestions/', api_views.AIViewSet.as_view({'get': 'suggestions'}), name='ai-suggestions'),
    path('ai/suggestions/live/', api_views.AIViewSet.as_view({'get': 'live_suggestions'}), name='ai-suggestions-live'),
    path('ai/enhance/', api_views.AIViewSet.as_view({'post': 'enhance_memory'}), name='ai-enhance'),
    path('ai/enhance-memory/', api_views.AIViewSet.as_view({'post': 'enhance_memory'}), name='ai-enhance-memory'),
    path('ai/categorize', api_views.AIViewSet.as_view({'post': 'categorize'}), name='ai-categorize'),
    path('ai/summarize', api_views.AIViewSet.as_view({'post': 'summarize'}), name='ai-summarize'),
    path('ai/tags', api_views.AIViewSet.as_view({'post': 'tags'}), name='ai-tags'),
    
    # Smart Reminder endpoints
    path('smart-reminders/analyze/', api_views.SmartReminderViewSet.as_view({'post': 'analyze'}), name='smart-reminder-analyze'),
    path('smart-reminders/scheduled/', api_views.SmartReminderViewSet.as_view({'get': 'scheduled'}), name='smart-reminder-scheduled'),
    path('smart-reminders/check/', api_views.SmartReminderViewSet.as_view({'post': 'check'}), name='smart-reminder-check'),
    path('smart-reminders/stats/', api_views.SmartReminderViewSet.as_view({'get': 'stats'}), name='smart-reminder-stats'),
    path('smart-reminders/update-scheduled/', api_views.SmartReminderViewSet.as_view({'post': 'update_scheduled'}), name='smart-reminder-update-scheduled'),
    path('smart-reminders/<int:pk>/dismiss/', api_views.SmartReminderViewSet.as_view({'post': 'dismiss'}), name='smart-reminder-dismiss'),
    path('smart-reminders/<int:pk>/snooze/', api_views.SmartReminderViewSet.as_view({'post': 'snooze'}), name='smart-reminder-snooze'),
    
    # Flutter-optimized endpoints
    path('', include(flutter_api_urls)),
]
