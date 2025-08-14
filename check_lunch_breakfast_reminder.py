#!/usr/bin/env python3
"""
Script to investigate the lunch and breakfast reminder issue
"""
import os
import sys
import django
from datetime import datetime, timedelta

# Setup Django environment
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'memora_project.settings')
django.setup()

from django.contrib.auth.models import User
from django.utils import timezone
from memory_assistant.models import Memory, SmartReminder, ReminderTrigger
from memory_assistant.smart_reminder_service import SmartReminderService

def check_lunch_breakfast_reminder():
    """Check for lunch and breakfast reminder and investigate the issue"""
    print("🔍 Investigating Lunch and Breakfast Reminder Issue")
    print("=" * 60)
    
    # Check all users
    users = User.objects.all()
    print(f"Found {users.count()} users")
    
    for user in users:
        print(f"\n👤 User: {user.username}")
        
        # Check for memories with lunch/breakfast content
        memories = Memory.objects.filter(
            user=user,
            content__icontains='lunch'
        ).union(
            Memory.objects.filter(
                user=user,
                content__icontains='breakfast'
            )
        )
        
        print(f"  Found {memories.count()} memories with lunch/breakfast content")
        
        for memory in memories:
            print(f"  📝 Memory ID {memory.id}: {memory.content[:100]}...")
            print(f"     Created: {memory.created_at}")
            print(f"     Delivery Date: {memory.delivery_date}")
            print(f"     Delivery Type: {memory.delivery_type}")
            print(f"     Memory Type: {memory.memory_type}")
            print(f"     Importance: {memory.importance}")
            
            # Check for smart reminders
            smart_reminders = SmartReminder.objects.filter(memory=memory)
            print(f"     Smart Reminders: {smart_reminders.count()}")
            
            for reminder in smart_reminders:
                print(f"       🔔 Reminder ID {reminder.id}:")
                print(f"         Type: {reminder.reminder_type}")
                print(f"         Priority: {reminder.priority}")
                print(f"         Active: {reminder.is_active}")
                print(f"         Next Trigger: {reminder.next_trigger}")
                print(f"         Last Triggered: {reminder.last_triggered}")
                print(f"         Trigger Conditions: {reminder.trigger_conditions}")
                
                # Check for triggers
                triggers = ReminderTrigger.objects.filter(reminder=reminder)
                print(f"         Triggers: {triggers.count()}")
                for trigger in triggers:
                    print(f"           📅 Trigger at {trigger.triggered_at}: {trigger.trigger_reason}")
    
    # Check current time and timezone
    now = timezone.now()
    print(f"\n⏰ Current Time: {now}")
    print(f"   Timezone: {now.tzinfo}")
    
    # Check for any reminders that should trigger around 8:35 PM
    print(f"\n🔍 Checking for reminders around 8:35 PM...")
    
    # Look for reminders that should trigger between 8:30-8:40 PM
    target_hour = 20  # 8 PM
    target_minute = 35
    
    # Check all active reminders
    active_reminders = SmartReminder.objects.filter(is_active=True)
    print(f"Found {active_reminders.count()} active reminders")
    
    for reminder in active_reminders:
        if reminder.next_trigger:
            reminder_time = reminder.next_trigger
            if reminder_time.tzinfo:
                reminder_time = reminder_time.astimezone(now.tzinfo)
            
            # Check if it's around 8:35 PM
            if (reminder_time.hour == target_hour and 
                abs(reminder_time.minute - target_minute) <= 5):
                print(f"  🎯 Found reminder at {reminder_time}:")
                print(f"     Memory: {reminder.memory.content[:50]}...")
                print(f"     User: {reminder.user.username}")
                print(f"     Type: {reminder.reminder_type}")
                print(f"     Should trigger: {reminder.should_trigger()}")
    
    # Test the reminder service
    print(f"\n🧪 Testing Smart Reminder Service...")
    reminder_service = SmartReminderService()
    
    # Check for triggered reminders
    triggered = reminder_service.check_and_trigger_reminders()
    print(f"Triggered {len(triggered)} reminders")
    
    for item in triggered:
        print(f"  🔔 Triggered: {item['reminder'].memory.content[:50]}...")
        print(f"     Reason: {item['trigger'].trigger_reason}")
        print(f"     Time: {item['trigger'].triggered_at}")

def create_test_lunch_breakfast_memory():
    """Create a test memory for lunch and breakfast reminder"""
    print(f"\n🧪 Creating Test Lunch and Breakfast Memory")
    print("=" * 50)
    
    # Get first user
    user = User.objects.first()
    if not user:
        print("❌ No users found")
        return
    
    print(f"Creating memory for user: {user.username}")
    
    # Create memory content
    content = "remember to buy lunch and breakfast for 8:35 p.m."
    
    # Create memory
    memory = Memory.objects.create(
        user=user,
        content=content,
        memory_type='reminder',
        importance=7,
        delivery_type='scheduled'
    )
    
    print(f"✅ Created memory ID {memory.id}")
    print(f"   Content: {memory.content}")
    
    # Process with smart reminder service
    reminder_service = SmartReminderService()
    suggestions = reminder_service.analyze_memory_for_reminders(memory)
    
    print(f"   Smart reminder suggestions: {len(suggestions)}")
    for suggestion in suggestions:
        print(f"     - {suggestion['description']}")
        print(f"       Type: {suggestion['type']}")
        print(f"       Priority: {suggestion['priority']}")
        print(f"       Conditions: {suggestion['trigger_conditions']}")
        
        # Create the reminder
        reminder = reminder_service.create_smart_reminder(memory, user, suggestion)
        if reminder:
            print(f"       ✅ Created reminder ID {reminder.id}")
            print(f"         Next trigger: {reminder.next_trigger}")
        else:
            print(f"       ❌ Failed to create reminder")

if __name__ == "__main__":
    check_lunch_breakfast_reminder()
    
    # Ask if user wants to create test memory
    response = input("\nWould you like to create a test lunch and breakfast memory? (y/n): ")
    if response.lower() == 'y':
        create_test_lunch_breakfast_memory()

