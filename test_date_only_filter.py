#!/usr/bin/env python3
"""
Test script for date-only filtering functionality
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

def test_date_only_filtering():
    """Test that date-only filtering works correctly"""
    print("🧪 Testing Date-Only Filtering Functionality")
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
    
    print(f"\n📅 Testing date-only filtering:")
    print(f"   Today: {today}")
    print(f"   Yesterday: {yesterday}")
    
    # Test filtering by yesterday (should have memories)
    yesterday_memories = all_memories.filter(created_at__date=yesterday)
    print(f"   Memories created yesterday: {yesterday_memories.count()}")
    
    if yesterday_memories.count() > 0:
        print("   ✅ Found memories from yesterday - good for testing!")
        
        # Test the exact logic from the view
        print(f"\n🔍 Testing view logic:")
        
        # Simulate the view logic
        query = ""  # No search query
        date_filter = yesterday.strftime('%Y-%m-%d')  # Date filter only
        
        print(f"   Query: '{query}'")
        print(f"   Date filter: '{date_filter}'")
        
        # Apply the same logic as in the view
        filtered_memories = Memory.objects.filter(
            user=user,
            is_archived=False
        )
        
        if date_filter:
            try:
                filter_date = datetime.strptime(date_filter, '%Y-%m-%d').date()
                filtered_memories = filtered_memories.filter(created_at__date=filter_date)
                print(f"   ✅ Date filter applied successfully")
            except ValueError as e:
                print(f"   ❌ Error parsing date: {e}")
        
        # Check if we should return date-only results
        if not query and date_filter:
            print(f"   ✅ Date-only filter condition met")
            print(f"   📊 Memories returned: {filtered_memories.count()}")
            
            if filtered_memories.count() == yesterday_memories.count():
                print("   ✅ Date-only filtering works correctly!")
            else:
                print("   ❌ Date-only filtering has issues!")
        else:
            print("   ❌ Date-only filter condition not met")
            
    else:
        print("   ⚠️  No memories from yesterday found - can't test date-only filtering")
        print("   💡 Try creating some test memories first")
    
    print(f"\n✅ Date-only filtering test completed!")

if __name__ == "__main__":
    test_date_only_filtering()
