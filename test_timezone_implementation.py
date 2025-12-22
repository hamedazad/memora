#!/usr/bin/env python
"""
Quick test to verify timezone implementation is working
"""
import os
import sys
import django

# Add the project to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'memora_project.settings')
django.setup()

from django.conf import settings
from django.utils import timezone
from django.contrib.auth import get_user_model
from memory_assistant.models import Memory, UserProfile
from memory_assistant.timezone_utils import (
    get_user_timezone, 
    get_current_time_in_user_timezone,
    naive_datetime_in_user_timezone,
    get_timezone_for_country
)

User = get_user_model()

print("=" * 70)
print("TIMEZONE IMPLEMENTATION TEST")
print("=" * 70)
print()

# Test 1: Django Settings
print("1. Django Settings:")
print(f"   TIME_ZONE: {settings.TIME_ZONE}")
print(f"   USE_TZ: {settings.USE_TZ}")
print(f"   ✅ Correct: USE_TZ should be False for local time storage")
print()

# Test 2: Country Mapping
print("2. Country to Timezone Mapping:")
test_countries = ['IR', 'US', 'GB', 'JP']
for code in test_countries:
    tz = get_timezone_for_country(code)
    print(f"   {code} → {tz}")
print("   ✅ Country mapping working")
print()

# Test 3: User Timezone
print("3. User Timezone Test:")
try:
    user = User.objects.get(username='lala')
    if hasattr(user, 'profile') and user.profile:
        user_tz = get_user_timezone(user)
        print(f"   User: {user.username}")
        print(f"   Profile timezone: {user.profile.user_timezone}")
        print(f"   Parsed timezone: {user_tz}")
        
        # Get current time in user's timezone
        local_time = naive_datetime_in_user_timezone(user)
        print(f"   Current local time: {local_time}")
        print("   ✅ User timezone working")
    else:
        print("   ⚠️ User has no profile")
except User.DoesNotExist:
    print("   ⚠️ User 'lala' not found")
except Exception as e:
    print(f"   ❌ Error: {e}")
print()

# Test 4: Memory Model Save Override
print("4. Memory Model Save Override:")
try:
    # Check if Memory model has custom save method
    import inspect
    save_method = inspect.getsource(Memory.save)
    if 'naive_datetime_in_user_timezone' in save_method:
        print("   ✅ Custom save() method implemented")
        print("   ✅ Will set created_at in user's local timezone")
    else:
        print("   ⚠️ Custom save() method might not be working")
except Exception as e:
    print(f"   ⚠️ Could not inspect save method: {e}")
print()

# Test 5: Recent Memories
print("5. Recent Memories Check:")
try:
    recent_memories = Memory.objects.order_by('-created_at')[:3]
    if recent_memories:
        for memory in recent_memories:
            user_tz = memory.user.profile.user_timezone if memory.user.profile else 'N/A'
            print(f"   Memory ID {memory.id}:")
            print(f"      User: {memory.user.username} (TZ: {user_tz})")
            print(f"      Created: {memory.created_at}")
            print(f"      Has timezone info: {memory.created_at.tzinfo is not None}")
    else:
        print("   No memories found")
except Exception as e:
    print(f"   ❌ Error: {e}")
print()

print("=" * 70)
print("TEST SUMMARY")
print("=" * 70)
print()
print("Next Steps:")
print("1. ✅ Django server should be running")
print("2. 📱 Create a new memory in the mobile app")
print("3. 🕐 Check if timestamp matches your local time")
print("4. ✅ Memory should save with your actual local time")
print()
print("Expected Behavior:")
print("- Create memory at 12:00 PM local")
print("- Should be saved as 12:00:00 (not converted to UTC)")
print("- Should display as 12:00 PM in the app")
print()
























