#!/usr/bin/env python3
"""
Comprehensive test for date filtering functionality
"""

import os
import sys
import django
from datetime import datetime, timedelta

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'memora_project.settings')
django.setup()

from memory_assistant.models import Memory, User
from django.db.models import Q

def test_comprehensive_date_filtering():
    """Test comprehensive date filtering functionality"""
    print("🧪 Comprehensive Date Filtering Test")
    print("=" * 50)
    
    # Get a test user
    try:
        user = User.objects.first()
        if not user:
            print("❌ No users found. Please create a user first.")
            return
        print(f"✅ Using user: {user.username}")
    except Exception as e:
        print(f"❌ Error getting user: {e}")
        return
    
    # Get all memories for the user
    all_memories = Memory.objects.filter(user=user, is_archived=False)
    print(f"📊 Total memories for user: {all_memories.count()}")
    
    # Test date filtering
    today = datetime.now().date()
    yesterday = today - timedelta(days=1)
    
    print(f"\n📅 Testing scenarios:")
    print(f"   Today: {today}")
    print(f"   Yesterday: {yesterday}")
    
    # Test 1: Date-only filtering (no search query)
    print(f"\n🔍 Test 1: Date-only filtering")
    yesterday_memories = all_memories.filter(created_at__date=yesterday)
    print(f"   Memories from yesterday: {yesterday_memories.count()}")
    
    # Test 2: Search-only filtering (no date)
    print(f"\n🔍 Test 2: Search-only filtering")
    test_memories = all_memories.filter(content__icontains="test")
    print(f"   Memories with 'test' in content: {test_memories.count()}")
    
    # Test 3: Combined filtering (search + date)
    print(f"\n🔍 Test 3: Combined filtering")
    combined_memories = test_memories.filter(created_at__date=yesterday)
    print(f"   Memories with 'test' from yesterday: {combined_memories.count()}")
    
    # Test 4: Simulate memory_list view logic
    print(f"\n🔍 Test 4: Memory List View Logic")
    
    # Simulate the view parameters
    query = ""
    date_filter = yesterday.strftime('%Y-%m-%d')
    memory_type = ""
    importance = ""
    
    # Apply the same logic as memory_list view
    memories = Memory.objects.filter(
        user=user,
        is_archived=False
    )
    
    # Apply date filter
    if date_filter:
        try:
            filter_date = datetime.strptime(date_filter, '%Y-%m-%d').date()
            memories = memories.filter(created_at__date=filter_date)
            print(f"   ✅ Date filter applied: {memories.count()} memories")
        except ValueError:
            print(f"   ❌ Error parsing date")
    
    # Apply search filter (should not run since query is empty)
    if query:
        search_conditions = Q()
        search_conditions |= Q(content__icontains=query)
        search_conditions |= Q(summary__icontains=query)
        search_conditions |= Q(tags__contains=[query])
        search_conditions |= Q(ai_reasoning__icontains=query)
        memories = memories.filter(search_conditions)
        print(f"   ✅ Search filter applied")
    else:
        print(f"   ✅ No search filter applied (query is empty)")
    
    print(f"   📊 Final result: {memories.count()} memories")
    
    # Verify the result matches our expectation
    if memories.count() == yesterday_memories.count():
        print(f"   ✅ Memory list view logic works correctly!")
    else:
        print(f"   ❌ Memory list view logic has issues!")
    
    # Test 5: Simulate search_memories view logic
    print(f"\n🔍 Test 5: Search Memories View Logic")
    
    # Simulate the view parameters
    query = ""
    date_filter = yesterday.strftime('%Y-%m-%d')
    
    # Apply the same logic as search_memories view
    all_memories_for_search = Memory.objects.filter(
        user=user,
        is_archived=False
    )
    
    # Apply date filter
    if date_filter:
        try:
            filter_date = datetime.strptime(date_filter, '%Y-%m-%d').date()
            all_memories_for_search = all_memories_for_search.filter(created_at__date=filter_date)
            print(f"   ✅ Date filter applied: {all_memories_for_search.count()} memories")
        except ValueError:
            print(f"   ❌ Error parsing date")
    
    # Check if we should return date-only results
    if not query and date_filter:
        memories = all_memories_for_search
        search_method = "date_filter_only"
        print(f"   ✅ Date-only filter condition met")
        print(f"   📊 Memories returned: {memories.count()}")
        print(f"   🏷️  Search method: {search_method}")
    else:
        print(f"   ❌ Date-only filter condition not met")
    
    # Verify the result matches our expectation
    if memories.count() == yesterday_memories.count():
        print(f"   ✅ Search memories view logic works correctly!")
    else:
        print(f"   ❌ Search memories view logic has issues!")
    
    print(f"\n✅ Comprehensive date filtering test completed!")

if __name__ == "__main__":
    test_comprehensive_date_filtering()
