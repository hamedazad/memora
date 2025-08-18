#!/usr/bin/env python
"""
Test Script for Enhanced Smart Reminder System with Scheduled Memories

This script demonstrates how the enhanced smart reminder system works with scheduled memories.
"""

import os
import sys
import django
from pathlib import Path
from datetime import datetime, timedelta

# Add the project directory to Python path
project_dir = Path(__file__).resolve().parent
sys.path.append(str(project_dir))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'memora_project.settings')
django.setup()

from django.contrib.auth.models import User
from memory_assistant.models import Memory
from memory_assistant.smart_reminder_service import SmartReminderService
from django.utils import timezone

def test_scheduled_memory_reminders():
    """Test the enhanced smart reminder system with scheduled memories"""
    
    print("🧪 Testing Enhanced Smart Reminder System")
    print("=" * 50)
    
    # Get or create a test user
    user, created = User.objects.get_or_create(
        username='testuser',
        defaults={
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User'
        }
    )
    
    if created:
        print(f"✅ Created test user: {user.username}")
    else:
        print(f"✅ Using existing test user: {user.username}")
    
    # Initialize the smart reminder service
    reminder_service = SmartReminderService()
    
    # Test 1: Create a scheduled memory with delivery_date
    print("\n📅 Test 1: Creating scheduled memory with delivery_date")
    
    # Create a memory due in 2 hours
    delivery_time = timezone.now() + timedelta(hours=2)
    
    scheduled_memory = Memory.objects.create(
        user=user,
        content="Important work meeting with the development team to discuss the new AI features implementation. Need to prepare presentation slides and review the technical specifications.",
        memory_type='work',
        importance=8,
        summary="Work meeting about AI features implementation",
        tags=['work', 'meeting', 'ai', 'development', 'presentation'],
        delivery_date=delivery_time,
        delivery_type='scheduled'
    )
    
    print(f"✅ Created scheduled memory: {scheduled_memory.content[:50]}...")
    print(f"   Due: {scheduled_memory.delivery_date.strftime('%Y-%m-%d %H:%M')}")
    print(f"   Type: {scheduled_memory.get_memory_type_display()}")
    print(f"   Importance: {scheduled_memory.importance}")
    
    # Test 2: Create smart reminder for scheduled memory
    print("\n🔔 Test 2: Creating smart reminder for scheduled memory")
    
    reminder = reminder_service.create_scheduled_memory_reminder(scheduled_memory, user)
    
    if reminder:
        print(f"✅ Created smart reminder:")
        print(f"   Type: {reminder.reminder_type}")
        print(f"   Priority: {reminder.priority}")
        print(f"   Next trigger: {reminder.next_trigger.strftime('%Y-%m-%d %H:%M')}")
        print(f"   Reason: {reminder.trigger_conditions.get('reason', 'N/A')}")
    else:
        print("❌ Failed to create smart reminder")
    
    # Test 3: Analyze memory for additional reminders
    print("\n🔍 Test 3: Analyzing memory for additional reminders")
    
    suggestions = reminder_service.analyze_memory_for_reminders(scheduled_memory)
    
    print(f"✅ Found {len(suggestions)} reminder suggestions:")
    for i, suggestion in enumerate(suggestions, 1):
        print(f"   {i}. {suggestion['description']}")
        print(f"      Type: {suggestion['type']}, Priority: {suggestion['priority']}")
    
    # Test 4: Create a recurring memory
    print("\n🔄 Test 4: Creating recurring memory")
    
    # Create a memory due tomorrow at 9 AM
    tomorrow_9am = timezone.now().replace(hour=9, minute=0, second=0, microsecond=0) + timedelta(days=1)
    
    recurring_memory = Memory.objects.create(
        user=user,
        content="Daily standup meeting with the team. Discuss progress, blockers, and plan for the day.",
        memory_type='work',
        importance=6,
        summary="Daily team standup meeting",
        tags=['work', 'meeting', 'daily', 'standup', 'team'],
        delivery_date=tomorrow_9am,
        delivery_type='recurring'
    )
    
    print(f"✅ Created recurring memory: {recurring_memory.content[:50]}...")
    print(f"   Due: {recurring_memory.delivery_date.strftime('%Y-%m-%d %H:%M')}")
    
    # Test 5: Get scheduled memory reminders
    print("\n📋 Test 5: Getting all scheduled memory reminders")
    
    scheduled_reminders = reminder_service.get_scheduled_memory_reminders(user)
    
    print(f"✅ Found {scheduled_reminders.count()} scheduled memory reminders:")
    for reminder in scheduled_reminders:
        memory = reminder.memory
        print(f"   📅 {memory.content[:40]}...")
        print(f"      Due: {memory.delivery_date.strftime('%Y-%m-%d %H:%M')}")
        print(f"      Reminder: {reminder.next_trigger.strftime('%Y-%m-%d %H:%M')}")
        print(f"      Priority: {reminder.priority}")
    
    # Test 6: Update scheduled memory
    print("\n🔄 Test 6: Updating scheduled memory delivery date")
    
    # Update the delivery date to 1 hour from now
    new_delivery_time = timezone.now() + timedelta(hours=1)
    scheduled_memory.delivery_date = new_delivery_time
    scheduled_memory.save()
    
    print(f"✅ Updated delivery date to: {new_delivery_time.strftime('%Y-%m-%d %H:%M')}")
    
    # Update the reminder
    reminder_service.update_scheduled_memory_reminders(scheduled_memory)
    
    # Check updated reminder
    updated_reminder = scheduled_memory.smart_reminders.first()
    if updated_reminder:
        print(f"✅ Updated reminder next trigger: {updated_reminder.next_trigger.strftime('%Y-%m-%d %H:%M')}")
    
    # Summary
    print("\n" + "=" * 50)
    print("🎉 Enhanced Smart Reminder System Test Complete!")
    print(f"📊 Total memories created: 2")
    print(f"🔔 Total reminders created: {user.smart_reminders.count()}")
    print(f"📅 Scheduled memories: {Memory.objects.filter(user=user, delivery_date__isnull=False).count()}")
    
    print("\n✨ Key Features Demonstrated:")
    print("   • Automatic reminder creation for scheduled memories")
    print("   • Intelligent advance notice based on importance and content")
    print("   • Support for recurring and conditional memories")
    print("   • Automatic reminder updates when delivery dates change")
    print("   • Priority-based reminder scheduling")
    print("   • Integration with existing smart reminder system")

if __name__ == "__main__":
    test_scheduled_memory_reminders()
