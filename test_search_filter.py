#!/usr/bin/env python3
"""
Test script to demonstrate improved search and filter functionality
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'memora_project.settings')
django.setup()

from memory_assistant.models import Memory
from django.contrib.auth.models import User
from django.db.models import Q

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
            "tags": ["meeting", "development", "feature", "project"],
            "ai_reasoning": "This is a work-related memory about a professional meeting"
        },
        {
            "content": "Need to buy groceries: milk, bread, eggs, and vegetables. Also pick up the dry cleaning.",
            "memory_type": "reminder",
            "importance": 6,
            "summary": "Shopping list and errands",
            "tags": ["shopping", "groceries", "errands", "dry cleaning"],
            "ai_reasoning": "This is a reminder for shopping and errands"
        },
        {
            "content": "Had a great dinner with family tonight. We talked about our upcoming vacation plans and shared stories from our childhood.",
            "memory_type": "personal",
            "importance": 7,
            "summary": "Family dinner and vacation planning",
            "tags": ["family", "dinner", "vacation", "childhood"],
            "ai_reasoning": "This is a personal memory about family time"
        },
        {
            "content": "Started learning Python programming today. Completed the basic syntax tutorial and built my first simple calculator program.",
            "memory_type": "learning",
            "importance": 9,
            "summary": "Learning Python programming basics",
            "tags": ["python", "programming", "learning", "tutorial"],
            "ai_reasoning": "This is a learning memory about programming education"
        },
        {
            "content": "Got an idea for a new mobile app that helps people track their daily habits and build better routines.",
            "memory_type": "idea",
            "importance": 8,
            "summary": "Creative idea for habit tracking app",
            "tags": ["idea", "mobile app", "habits", "routines"],
            "ai_reasoning": "This is a creative idea for a new application"
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
            tags=memory_data["tags"]
        )
        created_memories.append(memory)
        print(f"✅ Created memory {i}: {memory_data['memory_type']} - {memory_data['content'][:50]}...")
    
    print(f"\n📊 Total memories created: {len(created_memories)}")
    
    # Test different search scenarios
    search_tests = [
        {
            "query": "meeting",
            "description": "Search for work meetings",
            "expected_types": ["work"]
        },
        {
            "query": "shopping",
            "description": "Search for shopping-related content",
            "expected_types": ["reminder"]
        },
        {
            "query": "family",
            "description": "Search for family-related content",
            "expected_types": ["personal"]
        },
        {
            "query": "python",
            "description": "Search for programming content",
            "expected_types": ["learning"]
        },
        {
            "query": "app idea",
            "description": "Search for creative ideas",
            "expected_types": ["idea"]
        },
        {
            "query": "tomorrow",
            "description": "Search for time-related content",
            "expected_types": ["work", "reminder"]
        }
    ]
    
    print("\n🔍 Testing Search Functionality:")
    print("-" * 40)
    
    for test in search_tests:
        print(f"\n📝 Test: {test['description']}")
        print(f"Query: '{test['query']}'")
        
        # Test the search functionality
        search_conditions = Q()
        search_conditions |= Q(content__icontains=test['query'])
        search_conditions |= Q(summary__icontains=test['query'])
        search_conditions |= Q(tags__contains=[test['query']])
        search_conditions |= Q(ai_reasoning__icontains=test['query'])
        
        # Also search for individual words
        query_words = test['query'].split()
        for word in query_words:
            if len(word) >= 2:
                search_conditions |= Q(content__icontains=word)
                search_conditions |= Q(summary__icontains=word)
                search_conditions |= Q(tags__contains=[word])
        
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
    for memory_type in ['work', 'personal', 'learning', 'idea', 'reminder']:
        filtered = Memory.objects.filter(user=user, memory_type=memory_type, is_archived=False)
        print(f"  {memory_type.title()}: {filtered.count()} memories")
    
    # Test by importance
    print("\n⭐ Filter by Importance:")
    for importance in [5, 6, 7, 8, 9]:
        filtered = Memory.objects.filter(user=user, importance__gte=importance, is_archived=False)
        print(f"  {importance}+: {filtered.count()} memories")
    
    # Test combined filters
    print("\n🔗 Combined Filters:")
    
    # Work memories with importance 8+
    work_important = Memory.objects.filter(
        user=user, 
        memory_type='work', 
        importance__gte=8, 
        is_archived=False
    )
    print(f"  Work memories with importance 8+: {work_important.count()}")
    
    # Learning memories containing "python"
    python_learning = Memory.objects.filter(
        user=user,
        memory_type='learning',
        content__icontains='python',
        is_archived=False
    )
    print(f"  Learning memories about Python: {python_learning.count()}")
    
    # Test sorting
    print("\n📊 Testing Sorting:")
    
    # Sort by importance (descending)
    by_importance = Memory.objects.filter(user=user, is_archived=False).order_by('-importance')
    print(f"  Sorted by importance (highest first):")
    for memory in by_importance[:3]:
        print(f"    - {memory.importance}/10: {memory.content[:40]}...")
    
    # Sort by memory type
    by_type = Memory.objects.filter(user=user, is_archived=False).order_by('memory_type')
    print(f"  Sorted by memory type (A-Z):")
    for memory in by_type:
        print(f"    - {memory.memory_type}: {memory.content[:40]}...")
    
    print("\n" + "=" * 60)
    print("✅ Search & Filter Test Completed!")
    print("\nKey Improvements Demonstrated:")
    print("• Enhanced search across content, summary, tags, and AI reasoning")
    print("• Flexible word-based matching")
    print("• Multiple filter combinations")
    print("• Various sorting options")
    print("• Better search result feedback")
    
    # Clean up test data
    print("\n🧹 Cleaning up test data...")
    for memory in created_memories:
        memory.delete()
    print("✅ Test data cleaned up")

if __name__ == "__main__":
    test_search_filter_functionality() 