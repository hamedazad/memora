#!/usr/bin/env python
"""
Test AI Suggestions Script
Tests if AI suggestions are working properly.
"""

import os
import sys
import django
import time
from datetime import datetime

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'memora_project.settings')
django.setup()

from django.contrib.auth.models import User
from memory_assistant.models import Memory
from memory_assistant.services import ChatGPTService
from django.core.cache import cache

def test_ai_suggestions():
    """Test AI suggestions functionality"""
    print("🤖 Testing AI Suggestions")
    print("=" * 50)
    
    # Get or create test user
    user, created = User.objects.get_or_create(
        username='testuser',
        defaults={'email': 'test@example.com'}
    )
    if created:
        user.set_password('testpass123')
        user.save()
        print("Created test user: testuser")
    
    # Create some test memories if needed
    if Memory.objects.filter(user=user).count() < 3:
        print("Creating test memories...")
        Memory.objects.create(
            user=user,
            content="Meeting with team tomorrow at 10 AM to discuss project progress",
            memory_type='reminder',
            importance=8,
            tags=['meeting', 'work', 'project']
        )
        Memory.objects.create(
            user=user,
            content="Need to buy groceries: milk, bread, eggs, and vegetables",
            memory_type='shopping',
            importance=6,
            tags=['shopping', 'groceries']
        )
        Memory.objects.create(
            user=user,
            content="Doctor appointment next week on Tuesday at 2 PM",
            memory_type='reminder',
            importance=9,
            tags=['health', 'appointment']
        )
        print("Test memories created!")
    
    # Test ChatGPTService
    print("\n🔍 Testing ChatGPTService...")
    chatgpt_service = ChatGPTService()
    
    # Check if service is available
    is_available = chatgpt_service.is_available()
    print(f"ChatGPTService available: {is_available}")
    
    if not is_available:
        print("❌ ChatGPTService is not available. Check your API key.")
        return False
    
    # Get recent memories
    recent_memories = Memory.objects.filter(user=user, is_archived=False).order_by('-created_at')[:5]
    print(f"Found {recent_memories.count()} recent memories")
    
    if recent_memories.count() == 0:
        print("❌ No memories found. Cannot generate suggestions.")
        return False
    
    # Prepare memory data
    recent_memory_data = [
        {
            'content': memory.content,
            'tags': memory.tags or []
        } for memory in recent_memories
    ]
    
    print("\n📝 Recent memories:")
    for i, memory in enumerate(recent_memories, 1):
        print(f"  {i}. {memory.content[:50]}...")
    
    # Test generating suggestions
    print("\n💡 Generating AI suggestions...")
    try:
        start_time = time.time()
        suggestions = chatgpt_service.generate_memory_suggestions(recent_memory_data)
        generation_time = time.time() - start_time
        
        print(f"✅ Suggestions generated in {generation_time:.2f}s")
        print(f"Number of suggestions: {len(suggestions)}")
        
        print("\n🎯 AI Suggestions:")
        for i, suggestion in enumerate(suggestions, 1):
            print(f"  {i}. {suggestion}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error generating suggestions: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_cache_functionality():
    """Test caching of AI suggestions"""
    print(f"\n💾 Testing Cache Functionality")
    print("=" * 50)
    
    user = User.objects.get(username='testuser')
    
    # Clear cache
    cache.clear()
    print("Cache cleared")
    
    # Test cache key
    cache_key = f"ai_suggestions_{user.id}"
    print(f"Cache key: {cache_key}")
    
    # Check if cache is working
    cached_suggestions = cache.get(cache_key)
    print(f"Cached suggestions: {cached_suggestions}")
    
    # Test setting cache
    test_suggestions = ["Test suggestion 1", "Test suggestion 2"]
    cache.set(cache_key, test_suggestions, 600)
    print("Test suggestions cached")
    
    # Verify cache
    retrieved_suggestions = cache.get(cache_key)
    print(f"Retrieved suggestions: {retrieved_suggestions}")
    
    if retrieved_suggestions == test_suggestions:
        print("✅ Cache is working properly")
        return True
    else:
        print("❌ Cache is not working properly")
        return False

if __name__ == "__main__":
    print("🚀 Starting AI Suggestions Test")
    print(f"Time: {datetime.now()}")
    
    try:
        # Test AI suggestions
        ai_working = test_ai_suggestions()
        
        # Test cache functionality
        cache_working = test_cache_functionality()
        
        print(f"\n📊 Test Results:")
        print(f"  AI Suggestions: {'✅ WORKING' if ai_working else '❌ NOT WORKING'}")
        print(f"  Cache System: {'✅ WORKING' if cache_working else '❌ NOT WORKING'}")
        
        if ai_working and cache_working:
            print("\n✅ All tests passed! AI suggestions should work properly.")
        else:
            print("\n⚠️  Some tests failed. Check the issues above.")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()

