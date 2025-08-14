#!/usr/bin/env python
"""
Check the boss reminder timing
"""
import os
import sys
import django

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'memora_project.settings')
django.setup()

from django.utils import timezone
from memory_assistant.models import SmartReminder, Memory
from django.contrib.auth.models import User
from datetime import datetime, timedelta
import pytz

def check_boss_reminder():
    """Check the boss reminder timing"""
    print("=== Checking Boss Reminder ===")
    
    # Get current time
    now = timezone.now()
    print(f"Current UTC time: {now}")
    
    # Get user
    user = User.objects.get(username='hamed.azadkhah2@gmail.com')
    user_timezone = user.profile.user_timezone if hasattr(user, 'profile') else 'Asia/Tehran'
    user_tz = pytz.timezone(user_timezone)
    now_local = now.astimezone(user_tz)
    print(f"Current local time: {now_local}")
    
    # Find the boss reminder
    boss_reminders = SmartReminder.objects.filter(
        user=user,
        memory__content__icontains='boss',
        is_active=True
    ).select_related('memory')
    
    print(f"\nFound {boss_reminders.count()} boss reminders:")
    
    for reminder in boss_reminders:
        print(f"\n--- Reminder ID: {reminder.id} ---")
        print(f"Memory: {reminder.memory.content}")
        print(f"Next trigger (UTC): {reminder.next_trigger}")
        print(f"Next trigger (local): {reminder.next_trigger.astimezone(user_tz)}")
        print(f"Last triggered: {reminder.last_triggered}")
        print(f"Is active: {reminder.is_active}")
        
        # Calculate time until trigger
        time_until_trigger = reminder.next_trigger - now
        trigger_local = reminder.next_trigger.astimezone(user_tz)
        
        if time_until_trigger.total_seconds() > 0:
            print(f"⏰ Will trigger in: {time_until_trigger}")
            print(f"📅 Scheduled for: {trigger_local.date()}")
            print(f"🕐 At: {trigger_local.strftime('%H:%M:%S')}")
        else:
            print(f"⚠️  Should have triggered already!")
            print(f"Overdue by: {abs(time_until_trigger)}")
        
        # Check if it should trigger now
        if reminder.should_trigger():
            print(f"✅ Should trigger NOW!")
        else:
            print(f"⏳ Not ready to trigger yet")
    
    # Also check for any memories with "boss" in content
    boss_memories = Memory.objects.filter(
        user=user,
        content__icontains='boss'
    )
    
    print(f"\n=== Boss Memories ===")
    for memory in boss_memories:
        print(f"Memory ID: {memory.id}")
        print(f"Content: {memory.content}")
        print(f"Created: {memory.created_at}")
        print(f"Type: {memory.memory_type}")
        print("---")

if __name__ == "__main__":
    check_boss_reminder()
