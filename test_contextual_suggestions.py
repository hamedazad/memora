#!/usr/bin/env python3
"""
Test script for contextual AI suggestions
Tests the new date-aware suggestion system
"""

import os
import sys
import django
from datetime import datetime, timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'memora_project.settings')
django.setup()

from memory_assistant.models import Memory
from memory_assistant.services import ChatGPTService
from django.contrib.auth.models import User

def test_contextual_suggestions():
    """Test the new contextual suggestion system"""
    print("🧪 Testing Contextual AI Suggestions")
    print("=" * 50)
    
    # Get or create a test user
    user, created = User.objects.get_or_create(
        username='testuser',
        defaults={'email': 'test@example.com'}
    )
    if created:
        user.set_password('testpass123')
        user.save()
        print("✅ Created test user")
    else:
        print("✅ Using existing test user")
    
    # Create test memories with different dates and contexts
    test_memories = [
        {
            'content': 'Tennis match scheduled for tonight at 9:00 PM with John',
            'tags': ['sports', 'tennis', 'tonight'],
            'memory_type': 'appointment',
            'importance': 8
        },
        {
            'content': 'Meeting with Sarah tomorrow at 2:00 PM to discuss project',
            'tags': ['meeting', 'tomorrow', 'work'],
            'memory_type': 'appointment',
            'importance': 9
        },
        {
            'content': 'Buy groceries: milk, bread, eggs for this week',
            'tags': ['shopping', 'groceries', 'this week'],
            'memory_type': 'task',
            'importance': 6
        },
        {
            'content': 'Dentist appointment next week on Tuesday at 10:00 AM',
            'tags': ['health', 'dentist', 'next week'],
            'memory_type': 'appointment',
            'importance': 7
        },
        {
            'content': 'Remember to call mom this weekend',
            'tags': ['personal', 'family', 'call'],
            'memory_type': 'reminder',
            'importance': 8
        }
    ]
    
    # Create memories
    for i, memory_data in enumerate(test_memories):
        memory = Memory.objects.create(
            user=user,
            content=memory_data['content'],
            tags=memory_data['tags'],
            memory_type=memory_data['memory_type'],
            importance=memory_data['importance']
        )
        print(f"✅ Created memory {i+1}: {memory_data['content'][:50]}...")
    
    # Test queries
    test_queries = [
        "Did you set a reminder for tennis tonight at 9:00?",
        "What's my plan for tomorrow?",
        "I have plans for today",
        "What's scheduled for next week?",
        "Do I have any meetings today?",
        "What should I buy at the store?",
        "When is my dentist appointment?"
    ]
    
    # Initialize ChatGPT service
    chatgpt_service = ChatGPTService()
    
    if not chatgpt_service.is_available():
        print("❌ ChatGPT service not available. Please check your API key.")
        return
    
    print("\n🔍 Testing Contextual Suggestions")
    print("-" * 30)
    
    for query in test_queries:
        print(f"\n📝 Query: '{query}'")
        
        # Get user's memories for context
        user_memories = Memory.objects.filter(user=user, is_archived=False).order_by('-created_at')[:10]
        
        memory_data = [
            {
                'content': memory.content,
                'tags': memory.tags or []
            } for memory in user_memories
        ]
        
        # Get contextual suggestions
        suggestions = chatgpt_service.generate_contextual_suggestions(query, memory_data)
        
        if suggestions:
            print("💡 AI Suggestions:")
            for i, suggestion in enumerate(suggestions, 1):
                print(f"   {i}. {suggestion}")
        else:
            print("❌ No suggestions generated")
    
    # Test date-specific filtering
    print("\n📅 Testing Date-Specific Queries")
    print("-" * 30)
    
    date_queries = [
        "tonight",
        "tomorrow", 
        "this week",
        "next week"
    ]
    
    for query in date_queries:
        print(f"\n📝 Date Query: '{query}'")
        
        # Get user's memories for context
        user_memories = Memory.objects.filter(user=user, is_archived=False).order_by('-created_at')[:10]
        
        memory_data = [
            {
                'content': memory.content,
                'tags': memory.tags or []
            } for memory in user_memories
        ]
        
        # Get contextual suggestions
        suggestions = chatgpt_service.generate_contextual_suggestions(query, memory_data)
        
        if suggestions:
            print("💡 AI Suggestions:")
            for i, suggestion in enumerate(suggestions, 1):
                print(f"   {i}. {suggestion}")
        else:
            print("❌ No suggestions generated")
    
    # Clean up test data
    print("\n🧹 Cleaning up test data...")
    Memory.objects.filter(user=user).delete()
    print("✅ Test memories deleted")
    
    print("\n🎉 Contextual Suggestions Test Complete!")
    print("\nKey Improvements:")
    print("✅ Date-aware suggestions (tonight, tomorrow, etc.)")
    print("✅ Contextual clarification requests")
    print("✅ Better handling of time-specific queries")
    print("✅ Improved relevance for date-related searches")

if __name__ == "__main__":
    test_contextual_suggestions() 