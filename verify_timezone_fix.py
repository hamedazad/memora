#!/usr/bin/env python
"""
Verify that timezone settings are correct after the fix
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
from django.db import connection
from memory_assistant.models import Memory
from django.contrib.auth import get_user_model

User = get_user_model()

print("=" * 60)
print("TIMEZONE CONFIGURATION VERIFICATION")
print("=" * 60)
print()

# Check Django settings
print("1. Django Settings:")
print(f"   TIME_ZONE: {settings.TIME_ZONE}")
print(f"   USE_TZ: {settings.USE_TZ}")
print()

# Check current server time
print("2. Current Server Time:")
now = timezone.now()
print(f"   UTC: {now.strftime('%Y-%m-%d %H:%M:%S %Z')}")
print(f"   ISO Format: {now.isoformat()}")
print()

# Check database timezone
print("3. Database Configuration:")
with connection.cursor() as cursor:
    try:
        cursor.execute("SHOW timezone;")
        db_tz = cursor.fetchone()[0]
        print(f"   PostgreSQL Timezone: {db_tz}")
    except Exception as e:
        print(f"   Could not get DB timezone: {e}")
print()

# Check recent memory timestamps
print("4. Recent Memory Timestamps (Last 3):")
recent_memories = Memory.objects.order_by('-created_at')[:3]
for memory in recent_memories:
    print(f"   Memory ID {memory.id}:")
    print(f"      Created: {memory.created_at.isoformat()} ({memory.created_at.tzname()})")
    print(f"      User: {memory.user.username}")
    if memory.user.profile:
        print(f"      User Timezone: {memory.user.profile.timezone}")
    print()

# Check user profiles
print("5. User Profile Timezones:")
users_with_profiles = User.objects.filter(profile__isnull=False).select_related('profile')[:5]
for user in users_with_profiles:
    print(f"   {user.username}: {user.profile.timezone}")
print()

print("=" * 60)
print("VERIFICATION COMPLETE")
print("=" * 60)
print()
print("Expected Results:")
print("  - TIME_ZONE should be 'UTC'")
print("  - USE_TZ should be True")
print("  - Database timezone should be 'UTC' or 'Etc/UTC'")
print("  - All timestamps should have 'UTC' timezone")
print()
print("Next Steps:")
print("  1. If settings are correct, restart Django server")
print("  2. Create a new memory in the mobile app")
print("  3. Check if the timestamp is now correct")
print()
























