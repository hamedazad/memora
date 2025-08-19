from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
from . import api_views

# Create router for ViewSets
router = DefaultRouter()
router.register(r'memories', api_views.MemoryViewSet, basename='memory')
router.register(r'users', api_views.UserViewSet, basename='user')
router.register(r'ai', api_views.AIViewSet, basename='ai')

# API URL patterns
urlpatterns = [
    # Authentication endpoints
    path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    
    # Router URLs
    path('', include(router.urls)),
    
    # Additional endpoints
    path('memories/quick-add/', api_views.MemoryViewSet.as_view({'post': 'quick_add'}), name='memory-quick-add'),
    path('memories/search/', api_views.MemoryViewSet.as_view({'get': 'search'}), name='memory-search'),
    path('memories/dashboard-stats/', api_views.MemoryViewSet.as_view({'get': 'dashboard_stats'}), name='memory-dashboard-stats'),
    path('memories/<int:pk>/like/', api_views.MemoryViewSet.as_view({'post': 'like'}), name='memory-like'),
    path('memories/<int:pk>/comment/', api_views.MemoryViewSet.as_view({'post': 'comment'}), name='memory-comment'),
    
    # User endpoints
    path('users/profile/', api_views.UserViewSet.as_view({'get': 'profile'}), name='user-profile'),
    path('users/update-profile/', api_views.UserViewSet.as_view({'put': 'update_profile'}), name='user-update-profile'),
    
    # AI endpoints
    path('ai/suggestions/', api_views.AIViewSet.as_view({'get': 'suggestions'}), name='ai-suggestions'),
    path('ai/enhance-memory/', api_views.AIViewSet.as_view({'post': 'enhance_memory'}), name='ai-enhance-memory'),
]
