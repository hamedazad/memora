#!/usr/bin/env python3
"""
Test script for date filtering functionality
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

def test_date_filtering():
    """Test the date filtering functionality"""
    print("🧪 Testing Date Filtering Functionality")
    print("=" * 50)
    
    # Get a test user (create one if needed)
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
    tomorrow = today + timedelta(days=1)
    
    print(f"\n📅 Testing date filters:")
    print(f"   Today: {today}")
    print(f"   Yesterday: {yesterday}")
    print(f"   Tomorrow: {tomorrow}")
    
    # Test filtering by today
    today_memories = all_memories.filter(created_at__date=today)
    print(f"   Memories created today: {today_memories.count()}")
    
    # Test filtering by yesterday
    yesterday_memories = all_memories.filter(created_at__date=yesterday)
    print(f"   Memories created yesterday: {yesterday_memories.count()}")
    
    # Test filtering by tomorrow (should be 0)
    tomorrow_memories = all_memories.filter(created_at__date=tomorrow)
    print(f"   Memories created tomorrow: {tomorrow_memories.count()}")
    
    # Test combined search and date filtering
    print(f"\n🔍 Testing combined search and date filtering:")
    
    # Search for memories with "test" in content
    test_memories = all_memories.filter(content__icontains="test")
    print(f"   Memories with 'test' in content: {test_memories.count()}")
    
    # Combine search with date filter
    test_today_memories = test_memories.filter(created_at__date=today)
    print(f"   Memories with 'test' created today: {test_today_memories.count()}")
    
    # Test with specific date string format (like from form)
    date_string = today.strftime('%Y-%m-%d')
    print(f"\n📝 Testing with date string format: {date_string}")
    
    try:
        filter_date = datetime.strptime(date_string, '%Y-%m-%d').date()
        string_filtered_memories = all_memories.filter(created_at__date=filter_date)
        print(f"   Memories filtered by date string: {string_filtered_memories.count()}")
        
        if string_filtered_memories.count() == today_memories.count():
            print("   ✅ Date string filtering works correctly!")
        else:
            print("   ❌ Date string filtering has issues!")
            
    except ValueError as e:
        print(f"   ❌ Error parsing date string: {e}")
    
    print(f"\n✅ Date filtering test completed!")

if __name__ == "__main__":
    test_date_filtering()
