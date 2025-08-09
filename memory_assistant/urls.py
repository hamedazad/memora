from django.urls import path
from . import views
from . import views_ai
from . import views_social

app_name = 'memory_assistant'

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    
    # Memory CRUD
    path('memories/', views.memory_list, name='memory_list'),
    path('memories/create/', views.create_memory, name='create_memory'),
    path('memories/<int:memory_id>/', views.memory_detail, name='memory_detail'),
    path('memories/<int:memory_id>/edit/', views.edit_memory, name='edit_memory'),
    path('memories/<int:memory_id>/delete/', views.delete_memory, name='delete_memory'),
    path('memories/<int:memory_id>/archive/', views.archive_memory, name='archive_memory'),
    

    
    # Filtered Memory Views
    path('memories/all/', views.all_memories, name='all_memories'),
    path('memories/important/', views.important_memories, name='important_memories'),
    path('memories/scheduled/', views.scheduled_memories, name='scheduled_memories'),
    path('memories/today/', views.todays_memories, name='todays_memories'),

    

    
    # Search
    path('search/', views.search_memories, name='search_memories'),
    
    # Quick add (AJAX)
    path('quick-add/', views.quick_add_memory, name='quick_add_memory'),
    
    # Test memory (for demonstration)
    path('create-test-memory/', views.create_test_memory, name='create_test_memory'),
    
    # Debug endpoint
    path('debug-memories/', views.debug_memories, name='debug_memories'),
    
    # Voice features
    path('voice/create/', views.voice_create_memory, name='voice_create_memory'),
    path('voice/search/', views.voice_search_memories, name='voice_search_memories'),
    path('voice/read/<int:memory_id>/', views.voice_read_memory, name='voice_read_memory'),
    
    # AI Features
    path('ai/recommendations/', views.ai_recommendations, name='ai_recommendations'),
    path('ai/insights/', views.ai_insights, name='ai_insights'),
    path('ai/search-suggestions/', views.smart_search_suggestions, name='smart_search_suggestions'),
    
    # New AI Features
    path('ai/dashboard/', views_ai.ai_dashboard, name='ai_dashboard'),
    path('ai/enhance/', views_ai.ai_enhance_memory, name='ai_enhance_memory'),
    path('ai/categorize/', views_ai.ai_auto_categorize, name='ai_auto_categorize'),
    path('ai/tags/', views_ai.ai_generate_tags, name='ai_generate_tags'),
    path('ai/suggestions/', views_ai.ai_memory_suggestions, name='ai_memory_suggestions'),
    path('ai/related/<int:memory_id>/', views_ai.ai_related_memories, name='ai_related_memories'),
    
    # Authentication
    path('register/', views.register, name='register'),
    
    # Social Features
    
    # User Profiles
    path('social/profile/', views_social.profile_view, name='profile'),
    path('social/profile/edit/', views_social.edit_profile, name='edit_profile'),
    path('social/profile/<str:username>/', views_social.profile_view, name='profile'),
    
    # Friends
    path('social/friends/', views_social.friends_list, name='friends_list'),
    path('social/friends/find/', views_social.find_users, name='find_users'),
    path('social/friends/requests/', views_social.friend_requests, name='friend_requests'),
    path('social/friends/send/<int:user_id>/', views_social.send_friend_request, name='send_friend_request'),
    path('social/friends/respond/<int:request_id>/', views_social.respond_friend_request, name='respond_friend_request'),
    
    # Organizations
    path('social/organizations/', views_social.organizations_list, name='organizations_list'),
    path('social/organizations/<int:org_id>/', views_social.organization_detail, name='organization_detail'),
    path('social/organizations/create/', views_social.create_organization, name='create_organization'),
    
    # Organization Member Management
    path('social/organizations/<int:org_id>/members/', views_social.organization_members, name='organization_members'),
    path('social/organizations/<int:org_id>/invite/', views_social.invite_organization_member, name='invite_organization_member'),
    # Direct add disabled - use invitation system instead
    # path('social/organizations/<int:org_id>/add-member/', views_social.add_organization_member_direct, name='add_organization_member_direct'),
    path('social/organizations/<int:org_id>/remove/<int:member_id>/', views_social.remove_organization_member, name='remove_organization_member'),
    
    # Organization Invitation Management
    path('social/invitations/', views_social.my_organization_invitations, name='my_organization_invitations'),
    path('social/invitations/<int:invitation_id>/respond/', views_social.respond_organization_invitation, name='respond_organization_invitation'),
    
    # Memory Sharing
    path('social/share/<int:memory_id>/', views_social.share_memory, name='share_memory'),
    path('social/shared/', views_social.shared_with_me, name='shared_with_me'),
    
    # Memory Interactions
    path('social/comment/<int:memory_id>/', views_social.add_comment, name='add_comment'),
    path('social/like/<int:memory_id>/', views_social.toggle_like, name='toggle_like'),
    
    # Notifications
    path('social/notifications/', views_social.notifications, name='notifications'),
    path('social/notifications/count/', views_social.notifications_count, name='notifications_count'),
] 