#!/usr/bin/env python
"""Test script to verify future memory smart reminders work correctly"""

import os
import sys
import django
from datetime import datetime, timedelta
from django.utils import timezone

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'memora_project.settings')
django.setup()

from django.contrib.auth.models import User
from memory_assistant.models import Memory, SmartReminder
from memory_assistant.smart_reminder_service import SmartReminderService

def test_future_memory_reminders():
    """Test creating reminders for future scheduled memories"""
    print("\n" + "="*60)
    print("Testing Future Memory Smart Reminders")
    print("="*60)
    
    # Get or create test user
    try:
        user = User.objects.get(username='hamed')
        print(f"✓ Using existing user: {user.username}")
    except User.DoesNotExist:
        print("✗ User 'hamed' not found. Please create the user first.")
        return
    
    # Create a future scheduled memory
    future_time = timezone.now() + timedelta(hours=3)  # 3 hours from now
    
    test_memory = Memory.objects.create(
        user=user,
        content="Meeting with the team to discuss Q4 goals",
        memory_type='task',
        importance=8,
        delivery_date=future_time,
        delivery_type='scheduled',
        is_time_locked=True
    )
    print(f"\n✓ Created test memory: {test_memory.content[:50]}...")
    print(f"  Delivery date: {future_time}")
    print(f"  Importance: {test_memory.importance}")
    
    # Initialize the service
    service = SmartReminderService()
    
    # Test 1: Analyze memory for reminders
    print("\n" + "-"*40)
    print("Test 1: Analyzing memory for reminders")
    suggestions = service.analyze_memory_for_reminders(test_memory)
    
    if suggestions:
        print(f"✓ Found {len(suggestions)} suggestion(s):")
        for i, suggestion in enumerate(suggestions, 1):
            print(f"\n  Suggestion {i}:")
            print(f"    Type: {suggestion['type']}")
            print(f"    Priority: {suggestion['priority']}")
            print(f"    Description: {suggestion['description']}")
            
            trigger = suggestion['trigger_conditions']
            if 'advance_minutes' in trigger:
                print(f"    Advance notice: {trigger['advance_minutes']} minutes")
            if 'offset_minutes' in trigger:
                print(f"    Offset from now: {trigger['offset_minutes']} minutes")
            if 'reminder_time' in trigger:
                try:
                    reminder_time = datetime.fromisoformat(trigger['reminder_time'].replace('Z', '+00:00'))
                    print(f"    Reminder time: {reminder_time}")
                except:
                    pass
    else:
        print("✗ No suggestions found")
    
    # Test 2: Create scheduled memory reminder
    print("\n" + "-"*40)
    print("Test 2: Creating scheduled memory reminder")
    
    reminder = service.create_scheduled_memory_reminder(test_memory, user)
    
    if reminder:
        print(f"✓ Created reminder successfully:")
        print(f"  ID: {reminder.id}")
        print(f"  Type: {reminder.reminder_type}")
        print(f"  Priority: {reminder.priority}")
        print(f"  Next trigger: {reminder.next_trigger}")
        
        trigger_conditions = reminder.trigger_conditions
        if 'advance_minutes' in trigger_conditions:
            print(f"  Advance minutes: {trigger_conditions['advance_minutes']}")
        if 'offset_minutes' in trigger_conditions:
            print(f"  Offset minutes: {trigger_conditions['offset_minutes']}")
        
        # Verify the timing is correct
        if reminder.next_trigger:
            time_until_trigger = (reminder.next_trigger - timezone.now()).total_seconds() / 60
            print(f"\n  ⏰ Reminder will trigger in {time_until_trigger:.1f} minutes")
            
            # For meeting (60 minutes advance), should trigger 2 hours from now (3 hours - 1 hour)
            expected_minutes = 120  # 2 hours = 120 minutes
            if abs(time_until_trigger - expected_minutes) < 5:  # Allow 5 minute tolerance
                print(f"  ✓ Timing is correct (expected ~{expected_minutes} minutes)")
            else:
                print(f"  ✗ Timing seems off (expected ~{expected_minutes} minutes, got {time_until_trigger:.1f})")
    else:
        print("✗ Failed to create reminder")
    
    # Test 3: Update scheduled memory reminders
    print("\n" + "-"*40)
    print("Test 3: Testing update_scheduled_memory_reminders")
    
    # Change the delivery date to 5 hours from now
    new_future_time = timezone.now() + timedelta(hours=5)
    test_memory.delivery_date = new_future_time
    test_memory.save()
    print(f"✓ Updated memory delivery date to: {new_future_time}")
    
    # Update the reminder
    service.update_scheduled_memory_reminders(test_memory)
    
    # Reload the reminder
    if reminder:
        reminder.refresh_from_db()
        print(f"✓ Updated reminder:")
        print(f"  Next trigger: {reminder.next_trigger}")
        
        trigger_conditions = reminder.trigger_conditions
        if 'advance_minutes' in trigger_conditions:
            print(f"  Advance minutes: {trigger_conditions['advance_minutes']}")
        if 'offset_minutes' in trigger_conditions:
            print(f"  Offset minutes: {trigger_conditions['offset_minutes']}")
        
        # Verify the updated timing
        if reminder.next_trigger:
            time_until_trigger = (reminder.next_trigger - timezone.now()).total_seconds() / 60
            print(f"\n  ⏰ Reminder will now trigger in {time_until_trigger:.1f} minutes")
            
            # Should trigger 4 hours from now (5 hours - 1 hour advance)
            expected_minutes = 240  # 4 hours = 240 minutes
            if abs(time_until_trigger - expected_minutes) < 5:  # Allow 5 minute tolerance
                print(f"  ✓ Updated timing is correct (expected ~{expected_minutes} minutes)")
            else:
                print(f"  ✗ Updated timing seems off (expected ~{expected_minutes} minutes, got {time_until_trigger:.1f})")
    
    # Cleanup
    print("\n" + "-"*40)
    print("Cleaning up test data...")
    if reminder:
        reminder.delete()
    test_memory.delete()
    print("✓ Test data cleaned up")
    
    print("\n" + "="*60)
    print("Future Memory Reminder Tests Complete!")
    print("="*60)

if __name__ == '__main__':
    test_future_memory_reminders()

















































