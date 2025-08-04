from django.urls import path
from . import views
from . import views_ai

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
] 