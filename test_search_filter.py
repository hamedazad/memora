#!/usr/bin/env python3
"""
Test script to demonstrate improved search and filter functionality
"""

import os
import sys
import django
from datetime import datetime, timedelta

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'memora_project.settings')
django.setup()

from memory_assistant.models import Memory
from django.contrib.auth.models import User
from django.db.models import Q
from django.utils import timezone

def test_search_filter_functionality():
    """Test the enhanced search and filter functionality"""
    
    print("🔍 Testing Enhanced Search & Filter Functionality")
    print("=" * 60)
    
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
    
    # Create test memories with different types and content
    test_memories = [
        {
            "content": "Meeting with the development team tomorrow at 2 PM to discuss the new feature implementation and project timeline.",
            "memory_type": "work",
            "importance": 8,
            "summary": "Work meeting about new feature development",
            "tags": ["meeting", "development", "feature", "project", "tomorrow"],
            "ai_reasoning": "This is a work-related memory about a professional meeting scheduled for tomorrow",
            "scheduled_date": (timezone.now() + timedelta(days=1)).date()
        },
        {
            "content": "Need to buy groceries tomorrow: milk, bread, eggs, and vegetables. Also pick up the dry cleaning.",
            "memory_type": "reminder",
            "importance": 6,
            "summary": "Shopping list and errands for tomorrow",
            "tags": ["shopping", "groceries", "errands", "dry cleaning", "tomorrow"],
            "ai_reasoning": "This is a reminder for shopping and errands scheduled for tomorrow",
            "scheduled_date": (timezone.now() + timedelta(days=1)).date()
        },
        {
            "content": "Dentist appointment tomorrow at 10 AM. Need to bring insurance card and remember to floss tonight.",
            "memory_type": "reminder",
            "importance": 7,
            "summary": "Dentist appointment scheduled for tomorrow",
            "tags": ["dentist", "appointment", "health", "tomorrow"],
            "ai_reasoning": "This is a health-related reminder for a dentist appointment tomorrow",
            "scheduled_date": (timezone.now() + timedelta(days=1)).date()
        },
        {
            "content": "Planning to work on the new project tomorrow. Need to review the requirements and start coding the basic structure.",
            "memory_type": "work",
            "importance": 8,
            "summary": "Project work planned for tomorrow",
            "tags": ["work", "project", "coding", "planning", "tomorrow"],
            "ai_reasoning": "This is a work-related plan for tomorrow involving project development",
            "scheduled_date": (timezone.now() + timedelta(days=1)).date()
        },
        {
            "content": "Family dinner tomorrow evening. Mom is cooking her famous lasagna and we're all bringing side dishes.",
            "memory_type": "personal",
            "importance": 9,
            "summary": "Family dinner planned for tomorrow evening",
            "tags": ["family", "dinner", "lasagna", "tomorrow"],
            "ai_reasoning": "This is a personal memory about family plans for tomorrow evening",
            "scheduled_date": (timezone.now() + timedelta(days=1)).date()
        },
        {
            "content": "Had a great dinner with family tonight. We talked about our upcoming vacation plans and shared stories from our childhood.",
            "memory_type": "personal",
            "importance": 7,
            "summary": "Family dinner and vacation planning",
            "tags": ["family", "dinner", "vacation", "childhood"],
            "ai_reasoning": "This is a personal memory about family time",
            "scheduled_date": timezone.now().date()
        },
        {
            "content": "Started learning Python programming today. Completed the basic syntax tutorial and built my first simple calculator program.",
            "memory_type": "learning",
            "importance": 9,
            "summary": "Learning Python programming basics",
            "tags": ["python", "programming", "learning", "tutorial"],
            "ai_reasoning": "This is a learning memory about programming education",
            "scheduled_date": timezone.now().date()
        },
        {
            "content": "Got an idea for a new mobile app that helps people track their daily habits and build better routines.",
            "memory_type": "idea",
            "importance": 8,
            "summary": "Creative idea for habit tracking app",
            "tags": ["idea", "mobile app", "habits", "routines"],
            "ai_reasoning": "This is a creative idea for a new application",
            "scheduled_date": timezone.now().date()
        }
    ]
    
    # Create memories
    created_memories = []
    for i, memory_data in enumerate(test_memories, 1):
        memory = Memory.objects.create(
            user=user,
            content=memory_data["content"],
            memory_type=memory_data["memory_type"],
            importance=memory_data["importance"],
            summary=memory_data["summary"],
            ai_reasoning=memory_data["ai_reasoning"],
            tags=memory_data["tags"],
            scheduled_date=memory_data["scheduled_date"]
        )
        created_memories.append(memory)
        print(f"✅ Created memory {i}: {memory_data['memory_type']} - {memory_data['content'][:50]}...")
    
    print(f"\n📊 Total memories created: {len(created_memories)}")
    
    # Test natural language search queries
    print("\n\n🔍 Testing Natural Language Search Queries:")
    print("-" * 50)
    
    search_tests = [
        {
            "query": "what's the plan for tomorrow",
            "description": "Natural language query for tomorrow's plans",
            "expected_types": ["work", "reminder", "personal"]
        },
        {
            "query": "tomorrow",
            "description": "Simple date-based search",
            "expected_types": ["work", "reminder", "personal"]
        },
        {
            "query": "meeting",
            "description": "Search for meetings",
            "expected_types": ["work"]
        },
        {
            "query": "buy groceries",
            "description": "Shopping-related search",
            "expected_types": ["reminder"]
        },
        {
            "query": "dentist",
            "description": "Health appointment search",
            "expected_types": ["reminder"]
        },
        {
            "query": "family dinner",
            "description": "Personal activity search",
            "expected_types": ["personal"]
        },
        {
            "query": "work project",
            "description": "Work-related search",
            "expected_types": ["work"]
        },
        {
            "query": "call insurance",
            "description": "Phone call search",
            "expected_types": ["reminder"]
        }
    ]
    
    for test in search_tests:
        print(f"\n📝 Test: {test['description']}")
        print(f"Query: '{test['query']}'")
        
        # Test the enhanced search functionality
        search_conditions = Q()
        
        # Exact phrase match
        search_conditions |= Q(content__icontains=test['query'])
        search_conditions |= Q(summary__icontains=test['query'])
        search_conditions |= Q(ai_reasoning__icontains=test['query'])
        
        # Word-based matching
        query_words = test['query'].lower().split()
        for word in query_words:
            if len(word) >= 1:  # Allow single character words
                search_conditions |= Q(content__icontains=word)
                search_conditions |= Q(summary__icontains=word)
                search_conditions |= Q(tags__contains=[word])
                search_conditions |= Q(ai_reasoning__icontains=word)
        
        # Semantic variations
        semantic_variations = {
            'plan': ['plan', 'plans', 'planning', 'schedule', 'scheduled', 'arrange', 'arrangement'],
            'tomorrow': ['tomorrow', 'next day', 'day after', 'upcoming'],
            'today': ['today', 'tonight', 'this evening', 'now'],
            'meeting': ['meeting', 'appointment', 'call', 'conference', 'discussion'],
            'buy': ['buy', 'purchase', 'shop', 'shopping', 'get', 'pick up'],
            'call': ['call', 'phone', 'contact', 'dial', 'ring'],
            'work': ['work', 'job', 'office', 'professional', 'business'],
            'family': ['family', 'home', 'personal', 'kids', 'children'],
            'learn': ['learn', 'learning', 'study', 'education', 'tutorial'],
            'idea': ['idea', 'concept', 'thought', 'innovation', 'creative'],
            'what': ['what', 'when', 'where', 'how', 'why'],
            'the': ['the', 'a', 'an', 'this', 'that'],
            'for': ['for', 'to', 'with', 'about', 'regarding']
        }
        
        # Add semantic variations for words in the query
        for word in query_words:
            if word in semantic_variations:
                for variation in semantic_variations[word]:
                    search_conditions |= Q(content__icontains=variation)
                    search_conditions |= Q(summary__icontains=variation)
                    search_conditions |= Q(tags__contains=[variation])
                    search_conditions |= Q(ai_reasoning__icontains=variation)
        
        results = Memory.objects.filter(
            user=user,
            is_archived=False
        ).filter(search_conditions)
        
        print(f"Results found: {results.count()}")
        for memory in results:
            print(f"  - {memory.memory_type}: {memory.content[:60]}...")
        
        # Check if results match expected types
        found_types = set(memory.memory_type for memory in results)
        expected_types = set(test['expected_types'])
        
        if found_types.intersection(expected_types):
            print(f"  ✅ Found expected types: {found_types.intersection(expected_types)}")
        else:
            print(f"  ⚠️  No expected types found. Found: {found_types}")
    
    # Test filtering functionality
    print("\n\n🔧 Testing Filter Functionality:")
    print("-" * 40)
    
    # Test by memory type
    print("\n📋 Filter by Type:")
    for memory_type, _ in Memory.memory_type.field.choices:
        count = Memory.objects.filter(user=user, memory_type=memory_type, is_archived=False).count()
        if count > 0:
            print(f"  {memory_type}: {count} memories")
    
    # Test by importance
    print("\n⭐ Filter by Importance:")
    for importance in range(1, 11):
        count = Memory.objects.filter(user=user, importance__gte=importance, is_archived=False).count()
        if count > 0:
            print(f"  {importance}+: {count} memories")
    
    # Test by scheduled date
    print("\n📅 Filter by Scheduled Date:")
    tomorrow = (timezone.now() + timedelta(days=1)).date()
    today = timezone.now().date()
    
    tomorrow_count = Memory.objects.filter(user=user, scheduled_date=tomorrow, is_archived=False).count()
    today_count = Memory.objects.filter(user=user, scheduled_date=today, is_archived=False).count()
    
    print(f"  Tomorrow ({tomorrow}): {tomorrow_count} memories")
    print(f"  Today ({today}): {today_count} memories")
    
    print("\n✅ Search and filter testing completed!")
    print("\n💡 Try these queries in the web interface:")
    print("  - 'what's the plan for tomorrow'")
    print("  - 'meeting tomorrow'")
    print("  - 'buy groceries'")
    print("  - 'family dinner'")
    print("  - 'dentist appointment'")

if __name__ == "__main__":
    test_search_filter_functionality() 