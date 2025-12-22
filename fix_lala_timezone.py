#!/usr/bin/env python
"""
Fix lala user's timezone to Asia/Tehran
"""
import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'memora_project.settings')
django.setup()

from django.contrib.auth.models import User

print("=" * 60)
print("FIXING USER TIMEZONE")
print("=" * 60)
print()

try:
    user = User.objects.get(username='lala')
    
    print(f"User: {user.username}")
    print(f"OLD timezone: {user.profile.user_timezone}")
    print()
    
    # Update to Tehran timezone
    user.profile.user_timezone = 'Asia/Tehran'
    user.profile.save()
    
    print(f"NEW timezone: {user.profile.user_timezone}")
    print()
    print("✅ Timezone updated successfully!")
    print()
    print("Now when you create a memory:")
    print("- At 15:00 Tehran time")
    print("- Will save as 15:00")
    print("- Will display as 15:00 or '3:00 PM'")
    print()
    
except User.DoesNotExist:
    print("❌ User 'lala' not found")
except Exception as e:
    print(f"❌ Error: {e}")

print("=" * 60)
























