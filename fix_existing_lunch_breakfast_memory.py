#!/usr/bin/env python3
"""
Script to fix the existing lunch and breakfast memory with wrong delivery date
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
from memory_assistant.models import Memory, SmartReminder
from memory_assistant.smart_reminder_service import SmartReminderService

def fix_existing_lunch_breakfast_memory():
    """Fix the existing lunch and breakfast memory"""
    print("🔧 Fixing Existing Lunch and Breakfast Memory")
    print("=" * 50)
    
    # Find the existing memory with lunch and breakfast content
    memory = Memory.objects.filter(
        content__icontains='remember to buy lunch and breakfast for 8:35 p.m.'
    ).first()
    
    if not memory:
        print("❌ No existing lunch and breakfast memory found")
        return
    
    print(f"Found memory ID {memory.id}: {memory.content}")
    print(f"Current delivery date: {memory.delivery_date}")
    print(f"Current delivery type: {memory.delivery_type}")
    
    # Fix the delivery date to 8:35 PM (20:35)
    now = timezone.now()
    tomorrow = now + timedelta(days=1)
    correct_delivery_date = tomorrow.replace(hour=20, minute=35, second=0, microsecond=0)
    
    print(f"Fixing delivery date to: {correct_delivery_date}")
    
    # Update the memory
    memory.delivery_date = correct_delivery_date
    memory.delivery_type = 'scheduled'
    memory.save()
    
    print(f"✅ Updated memory delivery date")
    
    # Delete any existing smart reminders for this memory
    existing_reminders = SmartReminder.objects.filter(memory=memory)
    print(f"Deleting {existing_reminders.count()} existing reminders")
    existing_reminders.delete()
    
    # Create new smart reminders
    reminder_service = SmartReminderService()
    suggestions = reminder_service.analyze_memory_for_reminders(memory)
    
    print(f"Creating {len(suggestions)} new smart reminders")
    for suggestion in suggestions:
        print(f"  - {suggestion['description']}")
        print(f"    Type: {suggestion['type']}")
        print(f"    Priority: {suggestion['priority']}")
        
        # Create the reminder
        reminder = reminder_service.create_smart_reminder(memory, memory.user, suggestion)
        if reminder:
            print(f"    ✅ Created reminder ID {reminder.id}")
            print(f"      Next trigger: {reminder.next_trigger}")
            print(f"      Should trigger now: {reminder.should_trigger()}")
        else:
            print(f"    ❌ Failed to create reminder")
    
    # Check the final state
    print(f"\n📋 Final Memory State:")
    print(f"  Memory ID: {memory.id}")
    print(f"  Content: {memory.content}")
    print(f"  Delivery Date: {memory.delivery_date}")
    print(f"  Delivery Type: {memory.delivery_type}")
    
    reminders = SmartReminder.objects.filter(memory=memory)
    print(f"  Smart Reminders: {reminders.count()}")
    for reminder in reminders:
        print(f"    🔔 Reminder ID {reminder.id}:")
        print(f"      Type: {reminder.reminder_type}")
        print(f"      Active: {reminder.is_active}")
        print(f"      Next Trigger: {reminder.next_trigger}")
        print(f"      Should Trigger: {reminder.should_trigger()}")

if __name__ == "__main__":
    fix_existing_lunch_breakfast_memory()

