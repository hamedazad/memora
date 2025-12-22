#!/usr/bin/env python
"""
Update timezone for all users who should be in Iran/Tehran
"""
import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'memora_project.settings')
django.setup()

from django.contrib.auth.models import User

print("=" * 80)
print("UPDATE TIMEZONE FOR IRAN-BASED USERS")
print("=" * 80)
print()

# Get all users with profiles
users = User.objects.filter(profile__isnull=False).select_related('profile')

print(f"Found {users.count()} users with profiles")
print()

# List users with their current timezones
print("Current user timezones:")
print("-" * 80)
for user in users:
    tz = user.profile.user_timezone
    indicator = "✅" if tz == "Asia/Tehran" else "⚠️"
    print(f"{indicator} {user.username:20} → {tz}")

print()
print("-" * 80)
print()

# Ask which users to update
print("Which users should be updated to Asia/Tehran?")
print()
print("Options:")
print("1. Update ALL users to Asia/Tehran")
print("2. Update only specific users (you'll enter usernames)")
print("3. Skip - don't update anyone")
print()

choice = input("Enter your choice (1/2/3): ").strip()

if choice == "1":
    print()
    confirm = input("⚠️ Are you sure you want to update ALL users to Asia/Tehran? (yes/no): ").strip().lower()
    if confirm == "yes":
        updated_count = 0
        for user in users:
            if user.profile.user_timezone != "Asia/Tehran":
                old_tz = user.profile.user_timezone
                user.profile.user_timezone = "Asia/Tehran"
                user.profile.save()
                print(f"✅ Updated {user.username}: {old_tz} → Asia/Tehran")
                updated_count += 1
        print()
        print(f"✅ Updated {updated_count} users to Asia/Tehran")
    else:
        print("❌ Cancelled")

elif choice == "2":
    print()
    print("Enter usernames to update (comma-separated):")
    print("Example: azad,hamed,sajad")
    usernames_input = input("Usernames: ").strip()
    
    if usernames_input:
        usernames = [u.strip() for u in usernames_input.split(',')]
        updated_count = 0
        
        for username in usernames:
            try:
                user = User.objects.get(username=username, profile__isnull=False)
                old_tz = user.profile.user_timezone
                user.profile.user_timezone = "Asia/Tehran"
                user.profile.save()
                print(f"✅ Updated {user.username}: {old_tz} → Asia/Tehran")
                updated_count += 1
            except User.DoesNotExist:
                print(f"❌ User '{username}' not found or has no profile")
        
        print()
        print(f"✅ Updated {updated_count} users")
    else:
        print("❌ No usernames entered")

else:
    print("Skipped - no users updated")

print()
print("=" * 80)
print("DONE")
print("=" * 80)
print()
print("Next steps:")
print("1. New memories from updated users will save in Tehran time")
print("2. Test by creating a new memory")
print("3. Should match current Tehran time")
print()
























